import Grid from '@material-ui/core/Grid'
import { Link, navigate } from 'gatsby'
import React from 'react'
import { makeStyles } from '@material-ui/core/styles'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import Button from '@material-ui/core/Button'
import { getToken, removeToken } from 'src/jwt'

const useStyles = makeStyles(() => ({
  root: {
    flexGrow: 1,
  },
  link: {
    color: 'inherit',
    textDecoration: 'none',
    textTransform: 'none',
  },
}))

const Navbar = () => {
  const classes = useStyles()
  const token = getToken()

  function handleLogout() {
    removeToken()
    navigate('/login')
  }

  return (
    <AppBar position="fixed">
      <Toolbar>
        <Grid container spacing={1}>
          <Grid item>
            <Typography
              component={Link}
              variant="h6"
              to="/"
              className={classes.link}
            >
              Reposter
            </Typography>
          </Grid>
          <Grid item style={{ flexGrow: 1 }} />
          <Grid item>
            <Button component={Link} to="/reddit" className={classes.link}>
              reddit
            </Button>
          </Grid>
          <Grid item>
            <Button
              color="inherit"
              component="a"
              href="/admin"
              className={classes.link}
            >
              admin
            </Button>
          </Grid>
          <Grid item>
            {token ? (
              <Button onClick={handleLogout} className={classes.link}>
                logout
              </Button>
            ) : (
              <Button component={Link} to="/login" className={classes.link}>
                login
              </Button>
            )}
          </Grid>
        </Grid>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
