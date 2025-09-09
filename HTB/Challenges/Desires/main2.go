package main

import (
	"github.com/mholt/archiver/v3"
)

func main() {
	// 可透過find找路徑
	// find . -name payload.zip
	archiveFile := "./py2/payload.tar"
	destination := "./folder1a/folder2a"

	// Unarchive the zip file to the destination folder
	err := archiver.Unarchive(archiveFile, destination)
	if err != nil {
		print("Error in not null")
	}

}
