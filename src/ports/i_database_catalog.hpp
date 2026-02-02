// ports/i_database_catalog.hpp
#ifndef I_DATABASE_CATALOG_HPP
#define I_DATABASE_CATALOG_HPP

#include "ports/i_id_repository.hpp"
#include <memory>
#include <string>
#include <vector>

class IDatabaseCatalog {
public:
  virtual ~IDatabaseCatalog() = default;

  virtual void load_default_database() = 0;
  virtual bool create_database(const std::string &db_name_raw) = 0;
  virtual bool switch_to_database(const std::string &db_name) = 0;
  virtual bool database_exists(const std::string &db_name) const = 0;

  virtual IIdRepository *get_current_db() const = 0;
  virtual const std::string &get_current_db_name() const = 0;
  virtual std::vector<std::string> get_all_db_names() const = 0;
};

#endif
