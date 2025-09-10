package main

import (
	"fmt"

	"github.com/mholt/archiver/v3"
)

func main() {
	archiveFile := "./py3/payload.tar"
	destination := "./folder1b/folder2b"

	err := archiver.Unarchive(archiveFile, destination)
	if err != nil {
		fmt.Println("解壓縮失敗:", err)
	} else {
		fmt.Println("解壓縮成功")
	}
}
