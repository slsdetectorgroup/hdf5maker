#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

#include "raw_file.h"
#include "eiger_defs.h"
int dr_to_dtype(int dr) {
    switch (dr) {
    case 4:
        return NPY_UINT8;
    case 8:
        return NPY_UINT8;
    case 16:
        return NPY_UINT16;
    case 32:
        return NPY_UINT32;
    default:
        return NPY_UINT32; // fix
    }
}

void copy_to_place(uint8_t *dst, uint8_t *src, int dr, int row, int col){
    const size_t bytes_per_pixel = dr/8;
    const size_t bytes_per_row = PORT_NCOLS_WGAP * bytes_per_pixel;
    const size_t src_bytes_per_row = PORT_NCOLS * bytes_per_pixel;
    const size_t bytes_to_copy = NPIX_X_CHIP * bytes_per_pixel;

    int direction = 1;
    if (row%2){
        direction = -1;
        dst += bytes_per_row*(PORT_NROWS-1);
    }else{
        dst += bytes_per_row;
    }
    if(col%2)
        dst += bytes_per_pixel;

    for (int i = 0; i < PORT_NROWS; ++i) {
        memcpy(dst, src, bytes_to_copy);
        memcpy(dst+(NPIX_X_CHIP + 2)*bytes_per_pixel, src+NPIX_X_CHIP*bytes_per_pixel, bytes_to_copy);
        dst += bytes_per_row*direction;
        src += src_bytes_per_row;
    }
}