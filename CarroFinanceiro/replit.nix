{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.pandas
    pkgs.python311Packages.requests
    pkgs.python311Packages.pillow
    pkgs.python311Packages.cachetools
    pkgs.python311Packages.tenacity
    pkgs.zlib
    pkgs.tk
    pkgs.tcl
    pkgs.openjpeg
    pkgs.libxcrypt
    pkgs.libwebp
    pkgs.libtiff
    pkgs.libjpeg
    pkgs.libimagequant
    pkgs.lcms2
    pkgs.freetype
    pkgs.glibcLocales
  ];
}
