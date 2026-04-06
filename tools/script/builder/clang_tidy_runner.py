import concurrent.futures
import os
import shutil
import subprocess
import sys


def _resolve_jobs(requested_jobs):
    if requested_jobs and requested_jobs > 0:
        return requested_jobs
    env_jobs = os.environ.get("CLANG_TIDY_JOBS") or os.environ.get("CMAKE_BUILD_PARALLEL_LEVEL")
    if env_jobs:
        try:
            jobs = int(env_jobs)
            if jobs > 0:
                return jobs
        except ValueError:
            pass
    return max(1, os.cpu_count() or 1)


def _run_one(base_cmd, file_path):
    cmd = base_cmd + [file_path]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return file_path, proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return file_path, 127, "", f"clang-tidy not found: {base_cmd[0]}\n"


def _env_truthy(name, default=True):
    value = os.environ.get(name)
    if value is None:
        return default
    return str(value).strip().lower() not in {"0", "false", "no", "off"}


def _should_write_task(returncode, stdout, stderr):
    if returncode != 0:
        return True
    return bool((stdout or "").strip() or (stderr or "").strip())


def run_clang_tidy(args):
    if not args.files:
        print("--- clang-tidy: no source files provided.")
        return 0

    if not args.build_dir:
        print("--- !!! --build-dir is required for clang-tidy runner.", file=sys.stderr)
        return 1

    clang_tidy_exe = args.clang_tidy
    if not os.path.isabs(clang_tidy_exe):
        found = shutil.which(clang_tidy_exe)
        if not found:
            print(f"--- !!! clang-tidy executable not found: {clang_tidy_exe}", file=sys.stderr)
            return 1
        clang_tidy_exe = found

    build_dir = os.path.abspath(args.build_dir)
    compile_commands = os.path.join(build_dir, "compile_commands.json")
    if not os.path.isfile(compile_commands):
        print(f"--- !!! compile_commands.json not found in: {build_dir}", file=sys.stderr)
        print("--- 请先完成 CMake 配置并启用 CMAKE_EXPORT_COMPILE_COMMANDS。", file=sys.stderr)
        return 1

    split_logs = _env_truthy("CLANG_TIDY_SPLIT_LOGS", default=True)
    tasks_dir = os.path.abspath(args.tasks_dir) if args.tasks_dir else os.path.join(build_dir, "tasks")
    log_file = os.path.abspath(args.log_file) if args.log_file else os.path.join(build_dir, "build.log")

    base_cmd = [clang_tidy_exe, "-p", build_dir]
    if args.header_filter:
        base_cmd.append(f"-header-filter={args.header_filter}")
    if args.fix:
        base_cmd.append("-fix")
        if args.format_style:
            base_cmd.append(f"-format-style={args.format_style}")

    files = []
    seen = set()
    for path in args.files:
        norm = os.path.abspath(path)
        if norm in seen:
            continue
        seen.add(norm)
        files.append(norm)

    jobs = _resolve_jobs(args.jobs)
    if jobs > len(files):
        jobs = len(files)

    print(f"--- clang-tidy: {len(files)} files, {jobs} jobs", flush=True)

    failures = 0
    completed = 0
    results = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
        futures = {executor.submit(_run_one, base_cmd, file_path): file_path for file_path in files}
        for future in concurrent.futures.as_completed(futures):
            file_path, returncode, stdout, stderr = future.result()
            results[file_path] = (returncode, stdout, stderr)
            if stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
            if stderr:
                sys.stderr.write(stderr)
                sys.stderr.flush()
            completed += 1
            status = "OK" if returncode == 0 else f"FAIL({returncode})"
            print(f"[{completed}/{len(files)}] {status}: {file_path}", flush=True)
            if returncode != 0:
                failures += 1

    if split_logs:
        combined_lines = []
        file_index = 1
        task_index = 1
        index_lines = []
        for file_path in files:
            returncode, stdout, stderr = results.get(file_path, (1, "", "missing result\n"))
            status = "OK" if returncode == 0 else f"FAIL({returncode})"
            combined_lines.append(f"[{file_index:03d}] {status}: {file_path}\n")
            if stdout:
                combined_lines.append(stdout)
            if stderr:
                combined_lines.append(stderr)
            combined_lines.append("\n")

            if _should_write_task(returncode, stdout, stderr):
                os.makedirs(tasks_dir, exist_ok=True)
                task_name = f"task_{task_index:03d}.log"
                task_path = os.path.join(tasks_dir, task_name)
                header = [
                    f"File: {file_path}",
                    f"Status: {status}",
                    "=" * 60,
                    "",
                ]
                content = "\n".join(header) + (stdout or "") + (stderr or "")
                with open(task_path, "w", encoding="utf-8") as handle:
                    handle.write(content)
                index_lines.append(f"{task_name}\t{status}\t{file_path}")
                task_index += 1
            file_index += 1

        if combined_lines:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            with open(log_file, "w", encoding="utf-8") as handle:
                handle.write("".join(combined_lines))
        if index_lines and os.path.isdir(tasks_dir):
            index_path = os.path.join(tasks_dir, "index.txt")
            with open(index_path, "w", encoding="utf-8") as handle:
                handle.write("\n".join(index_lines) + "\n")

    return 1 if failures else 0
