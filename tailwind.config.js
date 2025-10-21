/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './*/templates/**/*.html',  // For app-level templates
    './static/**/*.js',
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [
    // require('daisyui'),
  ],
  // daisyui: {
  //   themes: ["light", "dark", "cupcake"], // Choose themes
  // },
}

