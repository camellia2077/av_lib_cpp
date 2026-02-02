// ports/i_id_repository.hpp
#ifndef I_ID_REPOSITORY_HPP
#define I_ID_REPOSITORY_HPP

#include <cstddef>
#include <string>
#include <vector>

class IIdRepository {
public:
  virtual ~IIdRepository() = default;

  virtual bool add(const std::string &id) = 0;
  virtual bool exists(const std::string &id) const = 0;
  virtual size_t get_count() const = 0;
  virtual std::vector<std::string> get_all_ids() const = 0;

  // Transaction control for bulk operations.
  virtual void begin_transaction() = 0;
  virtual void commit_transaction() = 0;
  virtual void rollback_transaction() = 0;
};

#endif
