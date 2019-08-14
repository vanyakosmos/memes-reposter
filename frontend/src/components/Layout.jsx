import { makeStyles } from '@material-ui/styles'
import { navigate } from 'gatsby'
import React, { useEffect, useState } from 'react'
import Container from '@material-ui/core/Container'
import Box from '@material-ui/core/Box'
import { authRefresh } from 'src/apiClient'
import { getToken, removeToken } from 'src/jwt'
import Navbar from './Navbar'

const useStyles = makeStyles(theme => ({
  pad: { ...theme.mixins.toolbar },
}))

export default function Layout({ children, protect = true }) {
  const classes = useStyles()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!protect) {
      setLoading(false)
      return
    }
    authRefresh(getToken())
      .then(() => {
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        removeToken()
        navigate('/login')
      })
  }, [])

  return (
    <div>
      <Navbar />
      <div className={classes.pad} />
      <Container maxWidth="sm">
        <Box my={4}>{loading ? null : children}</Box>
      </Container>
    </div>
  )
}
