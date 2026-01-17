package http

import (
	"net/http"
	"path/filepath"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	appconfig "mio-server/internal/config"
	"mio-server/internal/ws"
)

func NewRouter(cfg appconfig.Config, wsHandler *ws.Handler, logger *zap.Logger) *gin.Engine {
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(requestLogger(logger))

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	router.GET("/client-ws", func(c *gin.Context) {
		wsHandler.Handle(c.Writer, c.Request)
	})

	router.Static("/frontend", cfg.FrontendDir)
	router.Static("/assets", filepath.Join(cfg.FrontendDir, "assets"))
	router.Static("/live2d-models", cfg.Live2DModelsDir)
	router.Static("/libs", filepath.Join(cfg.FrontendDir, "libs"))
	router.Static("/backgrounds", cfg.BackgroundsDir)
	router.Static("/bg", cfg.BackgroundsDir)
	router.Static("/avatars", cfg.AvatarsDir)
	router.Static("/web-tool", cfg.WebToolDir)
	router.StaticFile("/", filepath.Join(cfg.FrontendDir, "index.html"))
	router.StaticFile("/favicon.ico", filepath.Join(cfg.FrontendDir, "favicon.ico"))

	return router
}

func requestLogger(logger *zap.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		c.Next()
		latency := time.Since(start)
		if logger == nil {
			return
		}
		logger.Info("http request",
			zap.String("method", c.Request.Method),
			zap.String("path", c.Request.URL.Path),
			zap.String("query", c.Request.URL.RawQuery),
			zap.String("client_ip", c.ClientIP()),
			zap.Int("status", c.Writer.Status()),
			zap.Int("bytes", c.Writer.Size()),
			zap.Duration("latency", latency),
			zap.String("user_agent", c.Request.UserAgent()),
		)
	}
}
