cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)

message(STATUS "CMAKE_BUILD_TYPE set to '${CMAKE_BUILD_TYPE}'")

# Source code
file(GLOB _pointers_SRC
    ${CMAKE_CURRENT_SOURCE_DIR}/src/_pointers/*.c
)
MESSAGE(DEBUG ${_pointers_SRC})

# Find Python
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# Link Python
python_add_library(_pointers MODULE ${_pointers_SRC} WITH_SOABI)

# Add include directories
target_include_directories(_pointers PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include/)

MESSAGE(STATUS "Everything looks good, let's install!")
# Install extension module
install(TARGETS _pointers DESTINATION .)
