const { defineConfig } = require('@vue/cli-service')

// https://vite.dev/config/
module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: './',
  devServer: {
    proxy: {
      '^/api': {
//        target: 'http://127.0.0.1:5000',
        target: 'http://192.168.169.134:5000',
        changeOrigin: true
      }
    }
  }
})
