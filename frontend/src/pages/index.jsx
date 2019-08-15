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
import { publishPosts } from 'src/apiClient'
import Layout from 'src/components/Layout'

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

function Action({ service, actionLabel, Input }) {
  const classes = useActionStyles()

  function handlePublish() {
    const blank = false // todo
    publishPosts(service, blank)
  }

  return (
    <Grid container alignItems="center" className={classes.root} spacing={1}>
      <Grid item className={classes.name}>
        <Typography variant="body1">{service}</Typography>
      </Grid>
      <Grid item className={classes.input}>
        <Input />
      </Grid>
      <Grid item>
        <Button color="secondary" onClick={handlePublish}>
          {actionLabel}
        </Button>
      </Grid>
    </Grid>
  )
}

function PublishAction({ service }) {
  const [bool, setBool] = useState(false)
  return (
    <Action
      service={service}
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

const CleanUpAction = ({ service, switchLabel = 'days' }) => {
  const [val, setVal] = useState(7)

  return (
    <Action
      service={service}
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

export default function IndexPage() {
  const classes = useStyles()
  return (
    <Layout>
      <Card className={classes.card}>
        <CardHeader title="Publish" />
        <CardContent>
          <PublishAction service="reddit" />
          <PublishAction service="imgur" />
          <PublishAction service="rss" />
        </CardContent>
      </Card>
      <Card className={classes.card}>
        <CardHeader title="Clean Up" />
        <CardContent>
          <CleanUpAction service="reddit" />
          <CleanUpAction service="imgur" />
          <CleanUpAction service="rss" switchLabel="keep" />
        </CardContent>
      </Card>
    </Layout>
  )
}
