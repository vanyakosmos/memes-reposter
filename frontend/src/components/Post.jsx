import { RootRef } from '@material-ui/core'
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
import React, { useEffect, useMemo, useRef, useState } from 'react'

const useStyles = makeStyles(({ palette }) => ({
  root: {
    position: 'relative',
    marginBottom: 20,
  },
  block: {
    marginBottom: 5,
  },
  link: {
    color: palette.secondary.main,
  },
}))

const useMediaStyles = makeStyles(() => ({
  media: {
    maxWidth: '100%',
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

function Image({ src, title }) {
  const classes = useMediaStyles()
  return (
    <a target="_blank" rel="noopener noreferrer" href={src}>
      <img src={src} alt={title} className={classes.media} />
    </a>
  )
}

function Video({ src, post }) {
  const classes = useMediaStyles()
  const ref = useRef(null)
  const update = useRef(0)
  const maxHeight = useMemo(() => {
    return window.innerHeight - 64
  }, [])

  useEffect(() => {
    function listener() {
      clearTimeout(update.current)
      update.current = setTimeout(() => {
        autoPlayVideo()
      }, 100)
    }
    window.addEventListener('scroll', listener)
    return () => {
      window.removeEventListener('scroll', listener)
    }
  })

  function autoPlayVideo() {
    const video = ref.current
    if (!video || !post) {
      return
    }
    let h = window.innerHeight
    let mid = window.scrollY + h / 2

    let bot = post.offsetTop + video.offsetTop
    let top = bot + video.clientHeight
    let videoMid = (bot + top) / 2
    bot = videoMid - h / 3
    top = videoMid + h / 3

    if (mid > bot && mid < top) {
      video.play()
    } else {
      video.pause()
    }
  }

  return (
    <video
      ref={ref}
      src={src}
      controls
      className={classes.media}
      style={{ maxHeight }}
    />
  )
}

export default function Post({
  id,
  title: defaultTitle,
  url,
  photo_url,
  video_url,
  subreddit_name,
  score,
  comments,
}) {
  const ref = useRef(null)
  const [title, setTitle] = useState(defaultTitle)
  const classes = useStyles()

  const photoUrl = useMemo(() => {
    if (photo_url) {
      return photo_url
    }
    if (!video_url && url && url.match(/.*\.gifv?/)) {
      return url
    }
    return null
  }, [photo_url, video_url])

  let post = null
  if (photoUrl) {
    post = <Image src={photoUrl} title={title} />
  } else if (video_url) {
    post = <Video src={video_url} post={ref.current} />
  }

  return (
    <RootRef rootRef={ref}>
      <Card className={classes.root} id={`post-${id}`}>
        <CardContent>
          {post && (
            <Grid container justify="center" className={classes.block}>
              {post}
            </Grid>
          )}
          <Grid
            container
            spacing={2}
            alignItems="center"
            className={classes.block}
            style={{ marginTop: 5 }}
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
    </RootRef>
  )
}
