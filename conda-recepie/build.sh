${PYTHON} setup.py install

mkdir -p $PREFIX/bin
cp $SRC_DIR/raw2hdf5 $PREFIX/bin/.

