module.exports = {
  siteMetadata: {
    title: `Reposter`,
    description: `reposter moderation site`,
    author: `@vanyakosmos`,
  },
  plugins: [
    `gatsby-plugin-root-import`,
    `gatsby-plugin-top-layout`,
    `gatsby-plugin-react-helmet`,
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/images`,
      },
    },
    `gatsby-transformer-sharp`,
    `gatsby-plugin-sharp`,
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: `gatsby-starter-default`,
        short_name: `reposter`,
        start_url: `/reddit`,
        background_color: `#1b1f21`,
        theme_color: `#1b1f21`,
        display: `minimal-ui`,
        icon: `src/images/gatsby-icon.png`, // This path is relative to the root of the site.
      },
    },
    `gatsby-plugin-material-ui`,
  ],
}
