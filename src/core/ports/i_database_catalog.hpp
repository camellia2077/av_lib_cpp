// core/ports/i_database_catalog.hpp
#ifndef I_DATABASE_CATALOG_HPP
#define I_DATABASE_CATALOG_HPP

#include <memory>
#include <string>
#include <vector>

#include "core/ports/i_id_repository.hpp"

class IDatabaseCatalog {
 public:
  virtual ~IDatabaseCatalog() = default;

  virtual void LoadDefaultDatabase() = 0;
  virtual auto CreateDatabase(const std::string& db_name_raw) -> bool = 0;
  virtual auto SwitchToDatabase(const std::string& db_name) -> bool = 0;
  [[nodiscard]] virtual auto DatabaseExists(const std::string& db_name) const
      -> bool = 0;

  [[nodiscard]] virtual auto GetCurrentDb() const -> IIdRepository* = 0;
  [[nodiscard]] virtual auto GetCurrentDbName() const -> const std::string& = 0;
  [[nodiscard]] virtual auto GetAllDbNames() const
      -> std::vector<std::string> = 0;
};

#endif
