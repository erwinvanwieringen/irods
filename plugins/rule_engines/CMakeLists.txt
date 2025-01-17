set(
  IRODS_RULE_ENGINE_PLUGIN-IRODS_RULE_LANGUAGE_SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/arithmetics.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/cache.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/configuration.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/conversion.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/datetime.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/filesystem.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/msiHelper.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/index.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/nre.reHelpers1.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/nre.reHelpers2.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/nre.reLib1.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/parser.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/reVariableMap.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/reVariableMap.gen.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/restructs.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/rules.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/typing.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/utils.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/rsRe.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/functions.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/libirods_rule_engine_plugin-irods_rule_language.cpp
  )

set(
  IRODS_RULE_ENGINE_PLUGIN-CPP_DEFAULT_POLICY_SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-cpp_default_policy/libirods_rule_engine_plugin-cpp_default_policy.cpp
  )

set(
  IRODS_RULE_ENGINE_PLUGIN-PASSTHROUGH_SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-passthrough/libirods_rule_engine_plugin-passthrough.cpp
  )

set(
  IRODS_RULE_ENGINE_PLUGINS
  irods_rule_engine_plugin-irods_rule_language
  irods_rule_engine_plugin-cpp_default_policy
  irods_rule_engine_plugin-passthrough
  )

foreach(PLUGIN ${IRODS_RULE_ENGINE_PLUGINS})
  string(TOUPPER ${PLUGIN} PLUGIN_UPPERCASE)

  add_library(
    ${PLUGIN}
    MODULE
    ${${PLUGIN_UPPERCASE}_SOURCES}
    )

  target_include_directories(
    ${PLUGIN}
    PRIVATE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/irods_rule_engine_plugin-irods_rule_language/include>
    ${IRODS_EXTERNALS_FULLPATH_BOOST}/include
    ${IRODS_EXTERNALS_FULLPATH_FMT}/include
    )

  target_link_libraries(
    ${PLUGIN}
    PRIVATE
    irods_server
    irods_common
    ${IRODS_EXTERNALS_FULLPATH_BOOST}/lib/libboost_filesystem.so
    ${IRODS_EXTERNALS_FULLPATH_BOOST}/lib/libboost_system.so
    ${IRODS_EXTERNALS_FULLPATH_BOOST}/lib/libboost_regex.so
    ${IRODS_EXTERNALS_FULLPATH_FMT}/lib/libfmt.so
    ${CMAKE_DL_LIBS}
    )

  target_compile_definitions(${PLUGIN} PRIVATE ${IRODS_COMPILE_DEFINITIONS} BOOST_SYSTEM_NO_DEPRECATED IRODS_ENABLE_SYSLOG)
  target_compile_options(${PLUGIN} PRIVATE -Wno-write-strings)
endforeach()

install(
  TARGETS
    ${IRODS_RULE_ENGINE_PLUGINS}
  LIBRARY
    DESTINATION ${IRODS_PLUGINS_DIRECTORY}/rule_engines
    COMPONENT ${IRODS_PACKAGE_COMPONENT_SERVER_NAME}
  )
