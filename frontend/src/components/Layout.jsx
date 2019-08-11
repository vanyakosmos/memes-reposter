import { makeStyles } from '@material-ui/styles'
import React from 'react'
import Container from '@material-ui/core/Container'
import Box from '@material-ui/core/Box'
import Navbar from './Navbar'

const useStyles = makeStyles(theme => ({
  pad: { ...theme.mixins.toolbar },
}))

const Layout = ({ children }) => {
  const classes = useStyles()
  return (
    <div>
      <Navbar />
      <div className={classes.pad} />
      <Container maxWidth="sm">
        <Box my={4}>{children}</Box>
      </Container>
    </div>
  )
}

export default Layout
