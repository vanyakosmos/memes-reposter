import Button from '@material-ui/core/Button'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import Grid from '@material-ui/core/Grid'
import CloseIcon from '@material-ui/icons/Close'
import RestoreIcon from '@material-ui/icons/Restore'
import IconButton from '@material-ui/core/IconButton'
import InputAdornment from '@material-ui/core/InputAdornment'
import TextField from '@material-ui/core/TextField'
import { makeStyles } from '@material-ui/styles'
import React, { useRef, useState } from 'react'

const useStyles = makeStyles(({ palette }) => ({
  root: {
    marginBottom: 20,
  },
  media: {
    maxWidth: '100%',
  },
  block: {
    marginBottom: 5,
  },
  link: {
    color: palette.secondary.main,
  },
}))

function TitleInput({ title, setTitle }) {
  const backup = useRef('')

  function handleClearTitle() {
    if (title) {
      backup.current = title
      setTitle('')
    } else {
      setTitle(backup.current)
    }
  }
  return (
    <TextField
      margin="dense"
      variant="outlined"
      value={title}
      onChange={e => setTitle(e.target.value)}
      fullWidth
      multiline
      rows={3}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <IconButton
              aria-label="toggle password visibility"
              onClick={handleClearTitle}
            >
              {title ? <CloseIcon /> : <RestoreIcon />}
            </IconButton>
          </InputAdornment>
        ),
      }}
    />
  )
}

export default function Post({
  title: defaultTitle,
  photo_url,
  subreddit_name,
  score,
  comments,
}) {
  const [title, setTitle] = useState(defaultTitle)
  const classes = useStyles()

  return (
    <Card className={classes.root}>
      <CardContent>
        <Grid container justify="center" className={classes.block}>
          {photo_url && (
            <a target="_blank" rel="noopener noreferrer" href={photo_url}>
              <img src={photo_url} alt={title} className={classes.media} />
            </a>
          )}
        </Grid>
        <Grid
          container
          spacing={2}
          alignItems="center"
          className={classes.block}
        >
          <Grid item>r/{subreddit_name}</Grid>
          <Grid item>{score}</Grid>
          <Grid item>
            <a
              href={comments}
              target="_blank"
              rel="noopener noreferrer"
              color="secondary"
              className={classes.link}
            >
              comments
            </a>
          </Grid>
          <Grid item style={{ flexGrow: 1 }} />
          <Grid item>{title.length}/200</Grid>
        </Grid>
        <div className={classes.block}>
          <TitleInput title={title} setTitle={setTitle} />
        </div>
        <Grid container justify="flex-end">
          <Grid item>
            <Button variant="contained" color="primary">
              publish
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
