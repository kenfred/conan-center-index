from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import re
import textwrap

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum"
    description = "Lightweight and modular C++11/C++14 graphics middleware for games and data visualization"
    license = "MIT"
    short_paths = True
    topics = ("magnum", "graphics", "middleware", "graphics", "rendering", "gamedev", "opengl", "3d", "2d", "opengl", "game-engine")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "shared_plugins": [True, False],

        # Follow documented build-options in https://doc.magnum.graphics/magnum/building.html#building-features
        #   Options like `with_xxxx` have been renamed to `xxxx`
        #   Options related to GL are being refactored into a choice option: gles2, gles3 or desktop_gl
        #   Some documented options are not available in sources: with_shaderstools, vk_info, with_shaderconverter and with_anyshaderconverter
        #   Option names are converted to snake_case

        "target_gl": ["gles2", "gles3", "desktop_gl", False],
        "target_headless": [True, False],
        "target_vk": [True, False],

        "audio": [True, False],
        "debug_tools": [True, False],
        "gl": [True, False],
        "mesh_tools": [True, False],
        "primitives": [True, False],
        "scene_graph": [True, False],
        "shaders": [True, False],
        "text": [True, False],
        "texture_tools": [True, False],
        "trade": [True, False],
        "vk": [True, False],
        
        "android_application": [True, False],
        "emscripten_application": [True, False],
        "glfw_application": [True, False],
        "glx_application": [True, False],
        "sdl2_application": [True, False],
        "xegl_application": [True, False],
        "windowless_cgl_application": [True, False],
        "windowless_egl_application": [True, False],
        "windowless_glx_application": [True, False],
        "windowless_ios_application": [True, False],
        "windowless_wgl_application": [True, False],
        "windowless_windows_egl_application": [True, False],

        "cgl_context": [True, False],
        "egl_context": [True, False],
        "glx_context": [True, False],
        "wgl_context": [True, False],

        "gl_info": [True, False],
        "al_info": [True, False],
        "distance_field_converter": [True, False],
        "font_converter": [True, False],
        "image_converter": [True, False],
        "scene_converter": [True, False],

        # Options related to plugins
        "any_audio_importer": [True, False],
        "any_image_converter": [True, False],
        "any_image_importer": [True, False],
        "any_scene_converter": [True, False],
        "any_scene_importer": [True, False],
        "magnum_font": [True, False],
        "magnum_font_converter": [True, False],
        "obj_importer": [True, False],
        "tga_importer": [True, False],
        "tga_image_converter": [True, False],
        "wav_audio_importer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,

        "target_gl": "desktop_gl",
        "target_headless": True,
        "target_vk": True,

        "audio": True,
        "debug_tools": True,
        "gl": True,
        "mesh_tools": True,
        "primitives": True,
        "scene_graph": True,
        "shaders": True,
        "text": True,
        "texture_tools": True,
        "trade": True,
        "vk": True,

        "android_application": True,
        "emscripten_application": True,
        "glfw_application": True,
        "glx_application": True,
        "sdl2_application": True,
        "xegl_application": True,
        "windowless_cgl_application": True,
        "windowless_egl_application": True,
        "windowless_glx_application": True,
        "windowless_ios_application": True,
        "windowless_wgl_application": True,
        "windowless_windows_egl_application": True,

        "cgl_context": True,
        "egl_context": True,
        "glx_context": True,
        "wgl_context": True,

        "gl_info": True,
        "al_info": True,
        "distance_field_converter": True,
        "font_converter": True,
        "image_converter": True,
        "scene_converter": True,

        # Related to plugins
        "any_audio_importer": True,
        "any_image_converter": True,
        "any_image_importer": True,
        "any_scene_converter": True,
        "any_scene_importer": True,
        "magnum_font": True,
        "magnum_font_converter": True,
        "obj_importer": True,
        "tga_importer": True,
        "tga_image_converter": True,
        "wav_audio_importer": True,
    }
    generators = "cmake", "cmake_find_package"
    exports_sources = ["CMakeLists.txt", "cmake/*"]
    
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def config_options(self):
        # Doc says that 'distance_field_converter' is only available with "desktop GL" (the same is said for 'font_converter', but it builds)
        # TODO: Here we probably have a CHOICE OPTION
        if self.options.target_gl in ["gles2", "gles3"]:
            del self.options.distance_field_converter

        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.egl_context
            del self.options.xegl_application
            del self.options.windowless_egl_application
            del self.options.windowless_ios_application
            del self.options.windowless_glx_application
            del self.options.windowless_windows_egl_application  # requires ANGLE
            del self.options.target_headless  # Requires EGL (when used gl_info)
            del self.options.glx_application
            del self.options.cgl_context
            del self.options.windowless_cgl_application

        if self.settings.os == "Linux":
            del self.options.cgl_context
            del self.options.windowless_cgl_application
            del self.options.wgl_context
            del self.options.windowless_wgl_application
            del self.options.windowless_windows_egl_application
        
        if self.settings.os == "Macos":
            del self.options.egl_context
            del self.options.glx_application  # Requires GL/glx.h (maybe XQuartz project)
            del self.options.xegl_application
            del self.options.windowless_egl_application
            del self.options.windowless_glx_application  # Requires GL/glx.h (maybe XQuartz project)
            del self.options.windowless_wgl_application
            del self.options.windowless_windows_egl_application
            del self.options.target_headless  # Requires EGL (when used gl_info)

        if self.settings.os != "Android":
            del self.options.android_application

        if self.settings.os != "Emscripten":
            del self.options.emscripten_application

        if self.settings.os != "iOS":
            del self.options.windowless_ios_application

    @property
    def _executables(self):
        #            (executable, option name)
        all_execs = (("gl-info", "gl_info"), 
                     ("al-info", "al_info"), 
                     ("distancefieldconverter", "distance_field_converter"), 
                     ("fontconverter", "font_converter"), 
                     ("imageconverter", "image_converter"), 
                     ("sceneconverter", "scene_converter"))
        return [executable for executable, opt_name in all_execs if self.options.get_safe(opt_name)]

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("corrade/{}".format(self.version))
        if self.options.audio:
            self.requires("openal/1.21.1")
        if self.options.gl:
            self.requires("opengl/system")
        if self.options.vk:
            self.requires("vulkan-loader/1.2.190")

        if self.options.get_safe("egl_context", False) or \
           self.options.get_safe("xegl_application", False) or \
           self.options.get_safe("windowless_egl_application", False) or \
           self.options.get_safe("windowless_ios_application") or \
           self.options.get_safe("windowless_windows_egl_application", False) or \
           self.options.get_safe("target_headless", False):
            self.requires("egl/system")

        if self.options.glfw_application:
            self.requires("glfw/3.3.4")

        if self.options.sdl2_application:
            self.requires("sdl/2.0.16")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        if self.settings.compiler == "gcc" and tools.Version(self.settings.compiler.version) < "5.0":
            raise ConanInvalidConfiguration("GCC older than 5 is not supported (missing C++11 features)")

        if self.options.shared and not self.options["corrade"].shared:
            # To fix issue with resource management, see here: https://github.com/mosra/magnum/issues/304#issuecomment-451768389
            raise ConanInvalidConfiguration("If using 'shared=True', corrade should be shared as well")

        if not self.options.gl and (self.options.target_gl or self.options.get_safe("target_headless", False)):
            raise ConanInvalidConfiguration("Option 'gl=True' is required")
        
        if self.options.target_gl in ["gles2", "gles3"] and self.settings.os == "Macos":
            raise ConanInvalidConfiguration("OpenGL ES is not supported in Macos")

        if self.options.target_gl in ["gles2", "gles3"] and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("OpenGL ES is not supported in Windows")        

        if not self.options.vk and self.options.target_vk:
            raise ConanInvalidConfiguration("Option 'vk=True' is required")

        if self.options.get_safe("cgl_context", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'cgl_context' requires some 'target_gl'")

        if self.options.get_safe("windowless_cgl_application", False) and not self.options.target_gl:
            raise ConanInvalidConfiguration("Option 'windowless_cgl_application' requires some 'target_gl'")

        if self.options.al_info and not self.options.audio:
            raise ConanInvalidConfiguration("Option 'al_info' requires 'audio=True'")

        if self.options.magnum_font_converter and not self.options.tga_image_converter:
            raise ConanInvalidConfiguration("magnum_font_converter requires tga_image_converter")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_DEPRECATED"] = False
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        # self._cmake.definitions["BUILD_STATIC_UNIQUE_GLOBALS"]
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared_plugins
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["BUILD_TESTS"] = False
        self._cmake.definitions["BUILD_GL_TESTS"] = False
        self._cmake.definitions["BUILD_AL_TESTS"] = False
        self._cmake.definitions["WITH_OPENGLTESTER"] = False
        self._cmake.definitions["WITH_VULKANTESTER"] = False

        self._cmake.definitions["TARGET_GL"] = bool(self.options.target_gl)
        self._cmake.definitions["TARGET_GLES"] = self.options.target_gl == "gles3"
        self._cmake.definitions["TARGET_GLES2"] = self.options.target_gl == "gles2"
        self._cmake.definitions["TARGET_DESKTOP_GLES"] = self.options.target_gl == "desktop_gl"
        self._cmake.definitions["TARGET_HEADLESS"] = self.options.get_safe("target_headless", False)
        self._cmake.definitions["TARGET_VK"] = self.options.target_vk

        self._cmake.definitions["WITH_AUDIO"] = self.options.audio
        self._cmake.definitions["WITH_DEBUGTOOLS"] = self.options.debug_tools
        self._cmake.definitions["WITH_GL"] = self.options.gl
        self._cmake.definitions["WITH_MESHTOOLS"] = self.options.mesh_tools
        self._cmake.definitions["WITH_PRIMITIVES"] = self.options.primitives
        self._cmake.definitions["WITH_SCENEGRAPH"] = self.options.scene_graph
        self._cmake.definitions["WITH_SHADERS"] = self.options.shaders
        self._cmake.definitions["WITH_TEXT"] = self.options.text
        self._cmake.definitions["WITH_TEXTURETOOLS"] = self.options.texture_tools
        self._cmake.definitions["WITH_TRADE"] = self.options.trade
        self._cmake.definitions["WITH_VK"] = self.options.vk

        self._cmake.definitions["WITH_ANDROIDAPPLICATION"] = self.options.get_safe("android_application", False)
        self._cmake.definitions["WITH_EMSCRIPTENAPPLICATION"] = self.options.get_safe("emscripten_application", False)
        self._cmake.definitions["WITH_GLFWAPPLICATION"] = self.options.glfw_application
        self._cmake.definitions["WITH_GLXAPPLICATION"] = self.options.get_safe("glx_application", False)
        self._cmake.definitions["WITH_SDL2APPLICATION"] = self.options.sdl2_application
        self._cmake.definitions["WITH_XEGLAPPLICATION"] = self.options.get_safe("xegl_application", False)
        self._cmake.definitions["WITH_WINDOWLESSCGLAPPLICATION"] = self.options.get_safe("windowless_cgl_application", False)
        self._cmake.definitions["WITH_WINDOWLESSEGLAPPLICATION"] = self.options.get_safe("windowless_egl_application", False)
        self._cmake.definitions["WITH_WINDOWLESSGLXAPPLICATION"] = self.options.get_safe("windowless_glx_application", False)
        self._cmake.definitions["WITH_WINDOWLESSIOSAPPLICATION"] = self.options.get_safe("windowless_ios_application", False)
        self._cmake.definitions["WITH_WINDOWLESSWGLAPPLICATION"] = self.options.get_safe("windowless_wgl_application", False)
        self._cmake.definitions["WITH_WINDOWLESSWINDOWSEGLAPPLICATION"] = self.options.get_safe("windowless_windows_egl_application", False)

        self._cmake.definitions["WITH_CGLCONTEXT"] = self.options.get_safe("cgl_context", False)
        self._cmake.definitions["WITH_EGLCONTEXT"] = self.options.get_safe("egl_context", False)
        self._cmake.definitions["WITH_GLXCONTEXT"] = self.options.glx_context
        self._cmake.definitions["WITH_WGLCONTEXT"] = self.options.get_safe("wgl_context", False)

        ##### Plugins related #####
        self._cmake.definitions["WITH_ANYAUDIOIMPORTER"] = self.options.any_audio_importer
        self._cmake.definitions["WITH_ANYIMAGECONVERTER"] = self.options.any_image_converter
        self._cmake.definitions["WITH_ANYIMAGEIMPORTER"] = self.options.any_image_importer
        self._cmake.definitions["WITH_ANYSCENECONVERTER"] = self.options.any_scene_converter
        self._cmake.definitions["WITH_ANYSCENEIMPORTER"] = self.options.any_scene_importer
        self._cmake.definitions["WITH_MAGNUMFONT"] = self.options.magnum_font
        self._cmake.definitions["WITH_MAGNUMFONTCONVERTER"] = self.options.magnum_font_converter
        self._cmake.definitions["WITH_OBJIMPORTER"] = self.options.obj_importer
        self._cmake.definitions["WITH_TGAIMPORTER"] = self.options.tga_importer
        self._cmake.definitions["WITH_TGAIMAGECONVERTER"] = self.options.tga_image_converter
        self._cmake.definitions["WITH_WAVAUDIOIMPORTER"] = self.options.wav_audio_importer

        #### Command line utilities ####
        self._cmake.definitions["WITH_GL_INFO"] = self.options.gl_info
        self._cmake.definitions["WITH_AL_INFO"] = self.options.al_info
        self._cmake.definitions["WITH_DISTANCEFIELDCONVERTER"] = self.options.get_safe("distance_field_converter", False)
        self._cmake.definitions["WITH_FONTCONVERTER"] = self.options.font_converter
        self._cmake.definitions["WITH_IMAGECONVERTER"] = self.options.image_converter
        self._cmake.definitions["WITH_SCENECONVERTER"] = self.options.scene_converter

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")
        # Get rid of cmake_dependent_option, it can activate features when we try to disable them,
        #   let the Conan user decide what to use and what not.
        with open(os.path.join(self._source_subfolder, "CMakeLists.txt"), 'r+') as f:
            text = f.read()
            text = re.sub('cmake_dependent_option\(([0-9A-Z_]+) .*\)', r'option(\1 "Option \1 disabled by Conan" OFF)', text)
            f.seek(0)
            f.write(text)
            f.truncate()

        # GLFW naming
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "find_package(GLFW)",
                              "find_package(glfw3)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "GLFW_FOUND",
                              "glfw3_FOUND")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "GLFW::GLFW",
                              "glfw::glfw")

        # EGL naming
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "find_package(EGL)",
                              "find_package(egl_system)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "EGL_FOUND",
                              "egl_system_FOUND")
        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Magnum", "Platform", "CMakeLists.txt"),
                              "EGL::EGL",
                              "egl::egl")

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        build_modules_folder = os.path.join(self.package_folder, "lib", "cmake")
        os.makedirs(build_modules_folder)
        for executable in self._executables:
            build_module_path = os.path.join(build_modules_folder, "conan-magnum-{}.cmake".format(executable))
            with open(build_module_path, "w+") as f:
                f.write(textwrap.dedent("""\
                    if(NOT TARGET Magnum::{exec})
                        if(CMAKE_CROSSCOMPILING)
                            find_program(MAGNUM_EXEC_PROGRAM magnum-{exec} PATHS ENV PATH NO_DEFAULT_PATH)
                        endif()
                        if(NOT MAGNUM_EXEC_PROGRAM)
                            set(MAGNUM_EXEC_PROGRAM "${{CMAKE_CURRENT_LIST_DIR}}/../../bin/magnum-{exec}")
                        endif()
                        get_filename_component(MAGNUM_EXEC_PROGRAM "${{MAGNUM_EXEC_PROGRAM}}" ABSOLUTE)
                        add_executable(Magnum::{exec} IMPORTED)
                        set_property(TARGET Magnum::{exec} PROPERTY IMPORTED_LOCATION ${{MAGNUM_EXEC_PROGRAM}})
                    endif()
                """.format(exec=executable)))

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("*.cmake", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join("lib", "cmake"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "Magnum"
        self.cpp_info.names["cmake_find_package_multi"] = "Magnum"

        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" else "magnum"
        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""

        # The FindMagnum.cmake file provided by the library populates some extra stuff
        self.cpp_info.components["_magnum"].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-vars.cmake"))

        # Magnum contains just the main library
        self.cpp_info.components["magnum_main"].names["cmake_find_package"] = "Magnum"
        self.cpp_info.components["magnum_main"].names["cmake_find_package_multi"] = "Magnum"
        self.cpp_info.components["magnum_main"].libs = ["Magnum{}".format(lib_suffix)]
        self.cpp_info.components["magnum_main"].requires = ["_magnum", "corrade::utility"]
        self.cpp_info.components["magnum_main"].build_modules["cmake_find_package"].append(os.path.join("lib", "cmake", "conan-bugfix-global-target.cmake"))

        # Audio
        if self.options.audio:
            self.cpp_info.components["audio"].names["cmake_find_package"] = "Audio"
            self.cpp_info.components["audio"].names["cmake_find_package_multi"] = "Audio"
            self.cpp_info.components["audio"].libs = ["MagnumAudio{}".format(lib_suffix)]
            self.cpp_info.components["audio"].requires = ["magnum_main", "corrade::plugin_manager", "openal::openal"]
            if self.options.scene_graph:
                self.cpp_info.components["audio"].requires += ["scene_graph"] 

        # DebugTools
        if self.options.debug_tools:
            self.cpp_info.components["debug_tools"].names["cmake_find_package"] = "DebugTools"
            self.cpp_info.components["debug_tools"].names["cmake_find_package_multi"] = "DebugTools"
            self.cpp_info.components["debug_tools"].libs = ["MagnumDebugTools{}".format(lib_suffix)]
            self.cpp_info.components["debug_tools"].requires = ["magnum_main"]
            if self.options["corrade"].with_testsuite and self.options.trade:
                self.cpp_info.components["debug_tools"].requires += ["corrade::test_suite", "trade"]

        # GL
        if self.options.gl:
            self.cpp_info.components["gl"].names["cmake_find_package"] = "GL"
            self.cpp_info.components["gl"].names["cmake_find_package_multi"] = "GL"
            self.cpp_info.components["gl"].libs = ["MagnumGL{}".format(lib_suffix)]
            self.cpp_info.components["gl"].requires = ["magnum_main", "opengl::opengl"]

        # MeshTools
        if self.options.mesh_tools:
            self.cpp_info.components["mesh_tools"].names["cmake_find_package"] = "MeshTools"
            self.cpp_info.components["mesh_tools"].names["cmake_find_package_multi"] = "MeshTools"
            self.cpp_info.components["mesh_tools"].libs = ["MagnumMeshTools{}".format(lib_suffix)]
            self.cpp_info.components["mesh_tools"].requires = ["magnum_main", "trade", "gl"]

        # Primitives
        if self.options.primitives:
            self.cpp_info.components["primitives"].names["cmake_find_package"] = "Primitives"
            self.cpp_info.components["primitives"].names["cmake_find_package_multi"] = "Primitives"
            self.cpp_info.components["primitives"].libs = ["MagnumPrimitives{}".format(lib_suffix)]
            self.cpp_info.components["primitives"].requires = ["magnum_main", "mesh_tools", "trade"]

        # SceneGraph
        if self.options.scene_graph:
            self.cpp_info.components["scene_graph"].names["cmake_find_package"] = "SceneGraph"
            self.cpp_info.components["scene_graph"].names["cmake_find_package_multi"] = "SceneGraph"
            self.cpp_info.components["scene_graph"].libs = ["MagnumSceneGraph{}".format(lib_suffix)]
            self.cpp_info.components["scene_graph"].requires = ["magnum_main"]

        # Shaders
        if self.options.shaders:
            self.cpp_info.components["shaders"].names["cmake_find_package"] = "Shaders"
            self.cpp_info.components["shaders"].names["cmake_find_package_multi"] = "Shaders"
            self.cpp_info.components["shaders"].libs = ["MagnumShaders{}".format(lib_suffix)]
            self.cpp_info.components["shaders"].requires = ["magnum_main", "gl"]

        # Text
        if self.options.text:
            self.cpp_info.components["text"].names["cmake_find_package"] = "Text"
            self.cpp_info.components["text"].names["cmake_find_package_multi"] = "Text"
            self.cpp_info.components["text"].libs = ["MagnumText{}".format(lib_suffix)]
            self.cpp_info.components["text"].requires = ["magnum_main", "texture_tools", "corrade::plugin_manager", "gl"]

        # TextureTools
        if self.options.texture_tools:
            self.cpp_info.components["texture_tools"].names["cmake_find_package"] = "TextureTools"
            self.cpp_info.components["texture_tools"].names["cmake_find_package_multi"] = "TextureTools"
            self.cpp_info.components["texture_tools"].libs = ["MagnumTextureTools{}".format(lib_suffix)]
            self.cpp_info.components["texture_tools"].requires = ["magnum_main"]
            if self.options.gl:
                self.cpp_info.components["texture_tools"].requires += ["gl"]

        # Trade
        if self.options.trade:
            self.cpp_info.components["trade"].names["cmake_find_package"] = "Trade"
            self.cpp_info.components["trade"].names["cmake_find_package_multi"] = "Trade"
            self.cpp_info.components["trade"].libs = ["MagnumTrade{}".format(lib_suffix)]
            self.cpp_info.components["trade"].requires = ["magnum_main", "corrade::plugin_manager"]

        # VK
        if self.options.vk:
            self.cpp_info.components["vk"].names["cmake_find_package"] = "Vk"
            self.cpp_info.components["vk"].names["cmake_find_package_multi"] = "Vk"
            self.cpp_info.components["vk"].libs = ["MagnumVk{}".format(lib_suffix)]
            self.cpp_info.components["vk"].requires = ["magnum_main", "vulkan-loader::vulkan-loader"]


        #### APPLICATIONS ####
        if self.options.get_safe("android_application", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("emscripten_application", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("windowless_ios_application", False):
            raise Exception("Recipe doesn't define this component")

        if self.options.get_safe("glx_application", False):
            self.cpp_info.components["glx_application"].names["cmake_find_package"] = "GlxApplication"
            self.cpp_info.components["glx_application"].names["cmake_find_package_multi"] = "GlxApplication"
            self.cpp_info.components["glx_application"].libs = ["MagnumGlxApplication{}".format(lib_suffix)]
            self.cpp_info.components["glx_application"].requires = ["gl"]  # TODO: Add x11

        if self.options.glfw_application:
            self.cpp_info.components["glfw_application"].names["cmake_find_package"] = "GlfwApplication"
            self.cpp_info.components["glfw_application"].names["cmake_find_package_multi"] = "GlfwApplication"
            self.cpp_info.components["glfw_application"].libs = ["MagnumGlfwApplication{}".format(lib_suffix)]
            self.cpp_info.components["glfw_application"].requires = ["magnum_main", "glfw::glfw"]
            if self.options.target_gl:
                self.cpp_info.components["glfw_application"].requires.append("gl")

        if self.options.sdl2_application:
            self.cpp_info.components["sdl2_application"].names["cmake_find_package"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].names["cmake_find_package_multi"] = "Sdl2Application"
            self.cpp_info.components["sdl2_application"].libs = ["MagnumSdl2Application{}".format(lib_suffix)]
            self.cpp_info.components["sdl2_application"].requires = ["magnum_main", "sdl::sdl"]
            if self.options.target_gl:
                self.cpp_info.components["sdl2_application"].requires += ["gl"]

        if self.options.get_safe("xegl_application", False):
            self.cpp_info.components["xegl_application"].names["cmake_find_package"] = "XEglApplication"
            self.cpp_info.components["xegl_application"].names["cmake_find_package_multi"] = "XEglApplication"
            self.cpp_info.components["xegl_application"].libs = ["MagnumXEglApplication{}".format(lib_suffix)]
            self.cpp_info.components["xegl_application"].requires = ["gl", "egl::egl"] # TODO: Add x11

        if self.options.get_safe("windowless_cgl_application", False):
            self.cpp_info.components["windowless_cgl_application"].names["cmake_find_package"] = "WindowlessCglApplication"
            self.cpp_info.components["windowless_cgl_application"].names["cmake_find_package_multi"] = "WindowlessCglApplication"
            self.cpp_info.components["windowless_cgl_application"].libs = ["MagnumWindowlessCglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_cgl_application"].requires = ["gl"]

        if self.options.get_safe("windowless_egl_application", False):
            self.cpp_info.components["windowless_egl_application"].names["cmake_find_package"] = "WindowlessEglApplication"
            self.cpp_info.components["windowless_egl_application"].names["cmake_find_package_multi"] = "WindowlessEglApplication"
            self.cpp_info.components["windowless_egl_application"].libs = ["MagnumWindowlessEglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_egl_application"].requires = ["gl", "egl::egl"]

        if self.options.get_safe("windowless_glx_application", False):
            self.cpp_info.components["windowless_glx_application"].names["cmake_find_package"] = "WindowlessGlxApplication"
            self.cpp_info.components["windowless_glx_application"].names["cmake_find_package_multi"] = "WindowlessGlxApplication"
            self.cpp_info.components["windowless_glx_application"].libs = ["MagnumWindowlessGlxApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_glx_application"].requires = ["gl"]  # TODO: Add x11

        if self.options.get_safe("windowless_wgl_application", False):
            self.cpp_info.components["windowless_wgl_application"].names["cmake_find_package"] = "WindowlessWglApplication"
            self.cpp_info.components["windowless_wgl_application"].names["cmake_find_package_multi"] = "WindowlessWglApplication"
            self.cpp_info.components["windowless_wgl_application"].libs = ["MagnumWindowlessWglApplication{}".format(lib_suffix)]
            self.cpp_info.components["windowless_wgl_application"].requires = ["gl"]

        if self.options.get_safe("windowless_windows_egl_application", False):
            raise Exception("Recipe doesn't define this component")

        """
            # If there is only one application, here it is an alias
            self.cpp_info.components["application"].names["cmake_find_package"] = "Application"
            self.cpp_info.components["application"].names["cmake_find_package_multi"] = "Application"
            self.cpp_info.components["application"].requires = ["sdl2_application"]
        """

        #### CONTEXTS ####
        if self.options.get_safe("cgl_context", False):
            self.cpp_info.components["cgl_context"].names["cmake_find_package"] = "CglContext"
            self.cpp_info.components["cgl_context"].names["cmake_find_package_multi"] = "CglContext"
            self.cpp_info.components["cgl_context"].libs = ["MagnumCglContext{}".format(lib_suffix)]
            self.cpp_info.components["cgl_context"].requires = ["gl"]

        if self.options.get_safe("egl_context", False):
            self.cpp_info.components["egl_context"].names["cmake_find_package"] = "EglContext"
            self.cpp_info.components["egl_context"].names["cmake_find_package_multi"] = "EglContext"
            self.cpp_info.components["egl_context"].libs = ["MagnumEglContext{}".format(lib_suffix)]
            self.cpp_info.components["egl_context"].requires = ["gl", "egl::egl"]

        if self.options.glx_context:
            self.cpp_info.components["glx_context"].names["cmake_find_package"] = "GlxContext"
            self.cpp_info.components["glx_context"].names["cmake_find_package_multi"] = "GlxContext"
            self.cpp_info.components["glx_context"].libs = ["MagnumGlxContext{}".format(lib_suffix)]
            self.cpp_info.components["glx_context"].requires = ["gl"]

        if self.options.get_safe("wgl_context", False):
            self.cpp_info.components["wgl_context"].names["cmake_find_package"] = "WglContext"
            self.cpp_info.components["wgl_context"].names["cmake_find_package_multi"] = "WglContext"
            self.cpp_info.components["wgl_context"].libs = ["MagnumWglContext{}".format(lib_suffix)]
            self.cpp_info.components["wgl_context"].requires = ["gl"]


        ######## PLUGINS ########
        if self.options.any_audio_importer:
            self.cpp_info.components["any_audio_importer"].names["cmake_find_package"] = "AnyAudioImporter"
            self.cpp_info.components["any_audio_importer"].names["cmake_find_package_multi"] = "AnyAudioImporter"
            self.cpp_info.components["any_audio_importer"].libs = ["AnyAudioImporter"]
            self.cpp_info.components["any_audio_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'audioimporters')]
            self.cpp_info.components["any_audio_importer"].requires = ["magnum_main", "audio"]

        if self.options.any_image_converter:
            self.cpp_info.components["any_image_converter"].names["cmake_find_package"] = "AnyImageConverter"
            self.cpp_info.components["any_image_converter"].names["cmake_find_package_multi"] = "AnyImageConverter"
            self.cpp_info.components["any_image_converter"].libs = ["AnyImageConverter"]
            self.cpp_info.components["any_image_converter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'imageconverters')]
            self.cpp_info.components["any_image_converter"].requires = ["trade"]

        if self.options.any_image_importer:
            self.cpp_info.components["any_image_importer"].names["cmake_find_package"] = "AnyImageImporter"
            self.cpp_info.components["any_image_importer"].names["cmake_find_package_multi"] = "AnyImageImporter"
            self.cpp_info.components["any_image_importer"].libs = ["AnyImageImporter"]
            self.cpp_info.components["any_image_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["any_image_importer"].requires = ["trade"]

        if self.options.any_scene_converter:
            self.cpp_info.components["any_scene_converter"].names["cmake_find_package"] = "AnySceneConverter"
            self.cpp_info.components["any_scene_converter"].names["cmake_find_package_multi"] = "AnySceneConverter"
            self.cpp_info.components["any_scene_converter"].libs = ["AnySceneConverter"]
            self.cpp_info.components["any_scene_converter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'sceneconverters')]
            self.cpp_info.components["any_scene_converter"].requires = ["trade"]

        if self.options.any_scene_importer:
            self.cpp_info.components["any_scene_importer"].names["cmake_find_package"] = "AnySceneImporter"
            self.cpp_info.components["any_scene_importer"].names["cmake_find_package_multi"] = "AnySceneImporter"
            self.cpp_info.components["any_scene_importer"].libs = ["AnySceneImporter"]
            self.cpp_info.components["any_scene_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["any_scene_importer"].requires = ["trade"]

        if self.options.magnum_font:
            self.cpp_info.components["magnum_font"].names["cmake_find_package"] = "MagnumFont"
            self.cpp_info.components["magnum_font"].names["cmake_find_package_multi"] = "MagnumFont"
            self.cpp_info.components["magnum_font"].libs = ["MagnumFont"]
            self.cpp_info.components["magnum_font"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'fonts')]
            self.cpp_info.components["magnum_font"].requires = ["magnum_main", "trade", "text"]

        if self.options.magnum_font_converter:
            self.cpp_info.components["magnum_font_converter"].names["cmake_find_package"] = "MagnumFontConverter"
            self.cpp_info.components["magnum_font_converter"].names["cmake_find_package_multi"] = "MagnumFontConverter"
            self.cpp_info.components["magnum_font_converter"].libs = ["MagnumFontConverter"]
            self.cpp_info.components["magnum_font_converter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'fontconverters')]
            self.cpp_info.components["magnum_font_converter"].requires = ["magnum_main", "trade", "text", "tga_image_converter"]

        if self.options.obj_importer:
            self.cpp_info.components["obj_importer"].names["cmake_find_package"] = "ObjImporter"
            self.cpp_info.components["obj_importer"].names["cmake_find_package_multi"] = "ObjImporter"
            self.cpp_info.components["obj_importer"].libs = ["ObjImporter"]
            self.cpp_info.components["obj_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["obj_importer"].requires = ["trade", "mesh_tools"]

        if self.options.tga_importer:
            self.cpp_info.components["tga_importer"].names["cmake_find_package"] = "TgaImporter"
            self.cpp_info.components["tga_importer"].names["cmake_find_package_multi"] = "TgaImporter"
            self.cpp_info.components["tga_importer"].libs = ["TgaImporter"]
            self.cpp_info.components["tga_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'importers')]
            self.cpp_info.components["tga_importer"].requires = ["trade"]

        if self.options.tga_image_converter:
            self.cpp_info.components["tga_image_converter"].names["cmake_find_package"] = "TgaImageConverter"
            self.cpp_info.components["tga_image_converter"].names["cmake_find_package_multi"] = "TgaImageConverter"
            self.cpp_info.components["tga_image_converter"].libs = ["TgaImageConverter"]
            self.cpp_info.components["tga_image_converter"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'imageconverters')]
            self.cpp_info.components["tga_image_converter"].requires = ["trade"]

        if self.options.wav_audio_importer:
            self.cpp_info.components["wav_audio_importer"].names["cmake_find_package"] = "WavAudioImporter"
            self.cpp_info.components["wav_audio_importer"].names["cmake_find_package_multi"] = "WavAudioImporter"
            self.cpp_info.components["wav_audio_importer"].libs = ["WavAudioImporter"]
            self.cpp_info.components["wav_audio_importer"].libdirs = [os.path.join(self.package_folder, 'lib', magnum_plugin_libdir, 'audioimporters')]
            self.cpp_info.components["wav_audio_importer"].requires = ["magnum_main", "audio"]

        #### EXECUTABLES ####
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        for executable in self._executables:
            self.cpp_info.components["_magnum"].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-{}.cmake".format(executable)))
