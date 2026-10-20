module.exports = {
  multipass: true,
  floatPrecision: 0,
  plugins: [
    { name: 'preset-default', params: { overrides: { convertPathData: { floatPrecision: 0, transformPrecision: 3 } } } },
  ],
};
