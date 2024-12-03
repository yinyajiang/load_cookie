package webviewloader

import (
	"crypto/tls"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/duke-git/lancet/v2/fileutil"
)

func httpClient() *http.Client {
	return &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
		},
	}
}

func downloadString(uri string) (string, error) {
	if !strings.HasPrefix(uri, "http") {
		return fileutil.ReadFileToString(uri)
	}

	client := httpClient()
	resp, err := client.Get(uri)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

func downloadFile(uri, path string) error {
	if !strings.HasPrefix(uri, "http") {
		fileutil.CreateDir(filepath.Dir(path))
		return fileutil.CopyFile(uri, path)
	}

	client := httpClient()
	resp, err := client.Get(uri)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	fileutil.CreateDir(filepath.Dir(path))

	out, err := os.Create(path)
	if err != nil {
		return err
	}
	defer out.Close()
	_, err = io.Copy(out, resp.Body)
	return err
}

func isWindows() bool {
	return strings.EqualFold(runtime.GOOS, "windows")
}

func findName(str string) string {
	str = strings.ReplaceAll(str, "\\", "/")
	arr := strings.Split(str, "/")
	return arr[len(arr)-1]
}

func findBaseName(str string) string {
	name := findName(str)
	dotIndex := strings.Index(name, ".")
	if dotIndex == -1 {
		return name
	}
	return name[:dotIndex]
}
