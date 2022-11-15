package main

// #cgo CFLAGS: -I.
// #cgo LDFLAGS: -L. -lpython-C
// #include "python-C.h"
import "C"

//make function available as exported C symbol

func PythonCallback() {
	C.Gocallback()
}

//export Pythoncall
func Pythoncall() uint {
	PythonCallback()
	return 9999
}

func main() {}

