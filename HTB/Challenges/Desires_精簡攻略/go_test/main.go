package main

import (
	"fmt"

	"github.com/mholt/archiver/v3"
)

func main() {
	zipTest()
	tarTest()
}

func zipTest() {
	// 可透過find找路徑
	// find . -name payload.zip
	archiveFile := "../py_test/zip_test/payload.zip"
	destination := "./zip1/zip2"

	// Unarchive the zip file to the destination folder
	err := archiver.Unarchive(archiveFile, destination)
	if err != nil {
		fmt.Println("zip解壓縮失敗:", err)
	} else {
		fmt.Println("zip解壓縮成功")
	}

	// [ERROR] Reading file in zip archive: checking path traversal attempt: illegal file path: ../../static/test.txt

}

func tarTest() {
	archiveFile := "../py_test/tar_test/payload.tar"
	destination := "./tar1/tar2"

	// Unarchive the zip file to the destination folder
	err := archiver.Unarchive(archiveFile, destination)
	if err != nil {
		fmt.Println("tar解壓縮失敗:", err)
	} else {
		fmt.Println("tar解壓縮成功")
	}

}
