module.exports = {
  multipass: true,
  floatPrecision: 1,
  plugins: [
    { name: 'preset-default', params: { overrides: { convertPathData: { floatPrecision: 1, transformPrecision: 3 } } } },
  ],
};
