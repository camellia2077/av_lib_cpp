// ports/i_id_repository.hpp
#ifndef I_ID_REPOSITORY_HPP
#define I_ID_REPOSITORY_HPP

#include <cstddef>
#include <string>
#include <vector>

class IIdRepository {
 public:
  virtual ~IIdRepository() = default;

  virtual auto Add(const std::string& id) -> bool = 0;
  [[nodiscard]] virtual auto Exists(const std::string& id) const -> bool = 0;
  [[nodiscard]] virtual auto GetCount() const -> size_t = 0;
  [[nodiscard]] virtual auto GetAllIds() const -> std::vector<std::string> = 0;

  // Transaction control for bulk operations.
  virtual void BeginTransaction() = 0;
  virtual void CommitTransaction() = 0;
  virtual void RollbackTransaction() = 0;
};

#endif
