package main

import (
	"github.com/mholt/archiver/v3"
)

func main() {
	// 可透過find找路徑
	// find . -name payload.zip
	archiveFile := "./py/payload.zip"
	destination := "./folder1/folder2"

	// Unarchive the zip file to the destination folder
	err := archiver.Unarchive(archiveFile, destination)
	if err != nil {
		print("Error in not null")
	}

	// [ERROR] Reading file in zip archive: checking path traversal attempt: illegal file path: ../../static/test.txt

}
