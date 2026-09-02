// webpack.config.js from watchCase
// test/watchCases/long-term-caching/css-contenthash-asset-url/webpack.config.js
// Present on squash merge; knobs match the failing world.
// realContentHash is false: [contenthash] is the module hash.

"use strict";

module.exports = {
  mode: "development",
  target: "web",
  node: {
    __dirname: false
  },
  output: {
    filename: "bundle.js",
    cssFilename: "[name].[contenthash].css",
    assetModuleFilename: "[name].[contenthash][ext]"
  },
  module: {
    rules: [
      {
        test: /\.png$/,
        type: "asset/resource"
      }
    ]
  },
  experiments: {
    css: true
  },
  optimization: {
    realContentHash: false
  }
};
