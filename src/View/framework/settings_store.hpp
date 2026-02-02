// view/framework/settings_store.hpp
#ifndef SETTINGS_STORE_HPP
#define SETTINGS_STORE_HPP

class SettingsStore {
public:
  virtual ~SettingsStore() = default;
  virtual void registerSettingsHandler() = 0;
};

#endif
