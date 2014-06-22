import os


def gen_build_ext(table={}):
    try:
        from Cython.Distutils import build_ext
        cython = True
    except ImportError:
        from setuptools.command.build_ext import build_ext
        cython = False

    class new_build_ext(build_ext):
        def build_extensions(self):
            for ext in self.extensions:
                self.translate(ext)
            build_ext.build_extensions(self)

        def translate(self, ext):
            if not cython:
                for i, source in enumerate(ext.sources):
                    if source.endswith('.pyx'):
                        base = os.path.splitext(source)[0]
                        for target_ext in ('.c', '.cpp'):
                            target = base + target_ext
                            if os.path.exists(target):
                                ext.sources[i] = target
                                break

            if self.compiler.compiler_type in table:
                trans = table[self.compiler.compiler_type]
            elif 'default' in table:
                trans = table['default']
            else:
                trans = {}
            for src, dst in trans.iteritems():
                ext.extra_compile_args[:] = [dst[0] if x == src else x for x in ext.extra_compile_args]
                ext.extra_link_args[:] = [dst[1] if x == src else x for x in ext.extra_link_args]
                ext.libraries[:] = [dst[2] if x == src else x for x in ext.libraries]

    return new_build_ext
