import Button from '@material-ui/core/Button'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import CardHeader from '@material-ui/core/CardHeader'
import Checkbox from '@material-ui/core/Checkbox'
import FormControlLabel from '@material-ui/core/FormControlLabel'
import Grid from '@material-ui/core/Grid'

import { makeStyles } from '@material-ui/core/styles'
import TextField from '@material-ui/core/TextField'
import Typography from '@material-ui/core/Typography'
import React, { useState } from 'react'
import Layout from '../components/Layout'

const useStyles = makeStyles({
  card: {
    marginBottom: 20,
  },
})

const useActionStyles = makeStyles({
  root: {
    marginBottom: 10,
  },
  name: {
    flexGrow: 1,
  },
  input: {
    maxWidth: 100,
  },
})

const Action = ({ label, actionLabel, Input }) => {
  const classes = useActionStyles()

  return (
    <Grid container alignItems="center" className={classes.root} spacing={1}>
      <Grid item className={classes.name}>
        <Typography variant="body1">{label}</Typography>
      </Grid>
      <Grid item className={classes.input}>
        <Input />
      </Grid>
      <Grid item>
        <Button color="secondary">{actionLabel}</Button>
      </Grid>
    </Grid>
  )
}

const PublishAction = ({ label }) => {
  const [bool, setBool] = useState(false)
  return (
    <Action
      label={label}
      actionLabel="publish"
      Input={() => (
        <FormControlLabel
          control={
            <Checkbox
              checked={bool}
              onChange={(e, v) => setBool(v)}
              color="secondary"
            />
          }
          label="blank"
        />
      )}
    />
  )
}

const CleanUpAction = ({ label, switchLabel = 'days' }) => {
  const [val, setVal] = useState(7)

  return (
    <Action
      label={label}
      actionLabel="clean up"
      Input={() => (
        <TextField
          label={switchLabel}
          value={val}
          onChange={e => setVal(e.target.value)}
          margin="dense"
          variant="outlined"
          type="number"
        />
      )}
    />
  )
}

const IndexPage = () => {
  const classes = useStyles()
  return (
    <Layout>
      <Card className={classes.card}>
        <CardHeader title="Publish" />
        <CardContent>
          <PublishAction label="reddit" />
          <PublishAction label="imgur" />
          <PublishAction label="rss" />
        </CardContent>
      </Card>
      <Card className={classes.card}>
        <CardHeader title="Clean Up" />
        <CardContent>
          <CleanUpAction label="reddit" />
          <CleanUpAction label="imgur" />
          <CleanUpAction label="rss" switchLabel="keep" />
        </CardContent>
      </Card>
    </Layout>
  )
}

export default IndexPage
