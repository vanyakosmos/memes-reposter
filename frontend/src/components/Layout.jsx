import React from "react"
import Container from "@material-ui/core/Container"
import Typography from "@material-ui/core/Typography"
import Box from "@material-ui/core/Box"
import Navbar from "./Navbar"

const Layout = ({ children }) => (
  <div>
    <Navbar />
    <Container maxWidth="sm">
      <Box my={4}>{children}</Box>
    </Container>
  </div>
)

export default Layout
