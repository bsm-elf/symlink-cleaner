package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"gopkg.in/natefinch/lumberjack.v2"
)

// Config structure
type Config struct {
	SymlinkDirs   []string `json:"symlink_dirs"`
	ZurgMount     string   `json:"zurg_mount"`
	DryRun        bool     `json:"dry_run"`
	EnableRemoval bool     `json:"enable_removal"`
	EnableRepair  bool     `json:"enable_repair"`
}

var (
	config      *Config
	configMutex sync.Mutex
)

// Default configuration values
var defaultConfig = Config{
	SymlinkDirs: []string{
		"/storage/symlinks/anime_movies/",
		"/storage/symlinks/anime_shows/",
		"/storage/symlinks/movies/",
		"/storage/symlinks/movies-4k/",
		"/storage/symlinks/series/",
		"/storage/symlinks/series-4k/",
	},
	ZurgMount:     "/storage/realdebrid-zurg/__all__/",
	DryRun:        true,
	EnableRemoval: true,
	EnableRepair:  true,
}

// Ensure log directory exists
func ensureLogDirectory() {
	logDir := "/app/logs"
	if err := os.MkdirAll(logDir, 0755); err != nil {
		log.Fatalf("Failed to create log directory: %v", err)
	}
}

// Initialize logging with rotation
func initLogging() {
	ensureLogDirectory()
	log.SetOutput(&lumberjack.Logger{
		Filename:   "/app/logs/backend.log",
		MaxSize:    10,
		MaxBackups: 5,
		MaxAge:     30,
		Compress:   true,
	})
	log.Println("Backend logging initialized with rotation.")
}

// Load configuration from JSON file and environment variables
func loadConfig(filename string) (*Config, error) {
	config := defaultConfig

	file, err := ioutil.ReadFile(filename)
	if err == nil {
		if err := json.Unmarshal(file, &config); err != nil {
			return nil, fmt.Errorf("error parsing config file: %v", err)
		}
	} else if !os.IsNotExist(err) {
		return nil, fmt.Errorf("error reading config file: %v", err)
	}

	if env := os.Getenv("ZURG_MOUNT"); env != "" {
		config.ZurgMount = env
	}
	if env := os.Getenv("DRY_RUN"); env != "" {
		config.DryRun = env == "true"
	}
	if env := os.Getenv("ENABLE_REMOVAL"); env != "" {
		config.EnableRemoval = env == "true"
	}
	if env := os.Getenv("ENABLE_REPAIR"); env != "" {
		config.EnableRepair = env == "true"
	}

	return &config, nil
}

func main() {
	ensureLogDirectory()
	initLogging()

	var err error
	config, err = loadConfig("config.json")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	log.Println("Starting server on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
