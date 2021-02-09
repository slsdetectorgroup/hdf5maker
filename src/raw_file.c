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

void insert_gap(char *dst, char *src, int dr, int row, int col){
    printf("row: %d, col: %d\n", row, col);
    const size_t bytes_per_pixel = dr/8;
    const size_t bytes_per_row = PORT_NCOLS_WGAP * bytes_per_pixel;
    const size_t bytes_to_copy = NPIX_X_CHIP * bytes_per_pixel;
    // if (!row%2)
    dst += bytes_per_row;

    printf("bytes_per_pixel: %d", bytes_per_pixel);
    if(col%2)
        dst += bytes_per_pixel;

    for (int i = 0; i < PORT_NROWS; ++i) {
        memcpy(dst, src, bytes_to_copy);
        src += NPIX_X_CHIP*bytes_per_pixel;
        dst += (NPIX_X_CHIP + 2)*bytes_per_pixel;
        memcpy(dst, src, bytes_to_copy);
        src += NPIX_X_CHIP*bytes_per_pixel;
        dst += (NPIX_X_CHIP + 1)*bytes_per_pixel;
    }

    // //Flip
    // if(row%2){
    //     char tmp = malloc(bytes_per_row);
    //     char* first_row = 

    //     free(tmp);

    // }


    return;
}