import { Card } from '@material-ui/core'
import Button from '@material-ui/core/Button'
import CardActions from '@material-ui/core/CardActions'
import CardContent from '@material-ui/core/CardContent'
import TextField from '@material-ui/core/TextField'
import { navigate } from 'gatsby'
import React, { useState } from 'react'
import { authObtain } from 'src/apiClient'
import Layout from 'src/components/Layout'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  function handlerChangeUsername(e) {
    setUsername(e.target.value)
  }

  function handlerChangePassword(e) {
    setPassword(e.target.value)
  }

  async function handleLogin() {
    await authObtain(username, password)
    navigate('/')
  }

  return (
    <Layout protect={false}>
      <Card style={{ maxWidth: 300, margin: '0 auto' }}>
        <CardContent>
          <TextField
            fullWidth
            margin="normal"
            label="username"
            value={username}
            onChange={handlerChangeUsername}
          />
          <TextField
            fullWidth
            margin="normal"
            label="password"
            value={password}
            onChange={handlerChangePassword}
            type="password"
          />
        </CardContent>
        <CardActions>
          <Button
            fullWidth
            onClick={handleLogin}
            variant="contained"
            color="secondary"
          >
            login
          </Button>
        </CardActions>
      </Card>
    </Layout>
  )
}
