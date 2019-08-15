import { Card } from '@material-ui/core'
import Button from '@material-ui/core/Button'
import CardContent from '@material-ui/core/CardContent'
import FormControl from '@material-ui/core/FormControl'
import Grid from '@material-ui/core/Grid'
import InputLabel from '@material-ui/core/InputLabel'
import MenuItem from '@material-ui/core/MenuItem'
import Select from '@material-ui/core/Select'
import useMediaQuery from '@material-ui/core/useMediaQuery'
import { makeStyles } from '@material-ui/styles'
import useTheme from '@material-ui/styles/useTheme'
import React, { useEffect, useRef, useState } from 'react'
import { getPendingSubreddits } from 'src/apiClient'

const useStyles = makeStyles({
  root: {
    marginBottom: 20,
    position: 'sticky',
    top: props => props.top,
    zIndex: 10,
    opacity: 0.9,
  },
})

function OrderingSelect({ ordering, setOrdering }) {
  return (
    <FormControl fullWidth>
      <InputLabel htmlFor="order-select">sort by</InputLabel>
      <Select
        value={ordering}
        onChange={e => setOrdering(e.target.value)}
        inputProps={{
          id: 'order-select',
          name: 'order',
        }}
      >
        <MenuItem value="created">created asc</MenuItem>
        <MenuItem value="-created">created desc</MenuItem>
        <MenuItem value="score">score asc</MenuItem>
        <MenuItem value="-score">score desc</MenuItem>
      </Select>
    </FormControl>
  )
}

function SubredditSelect({ subreddit, setSubreddit }) {
  const [subs, setSubs] = useState([])

  useEffect(() => {
    getPendingSubreddits().then(subs => {
      setSubs(subs)
    })
  }, [])

  return (
    <FormControl fullWidth>
      <InputLabel htmlFor="subreddit-select">subreddit</InputLabel>
      <Select
        value={subreddit}
        onChange={e => setSubreddit(e.target.value)}
        inputProps={{
          id: 'subreddit-select',
          name: 'subreddit',
        }}
      >
        <MenuItem value={'-'}>---</MenuItem>
        {subs.map(s => (
          <MenuItem key={s} value={s}>
            {s}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}

export default function Filters({
  ordering,
  onSetOrdering,
  subreddit,
  onSetSubreddit,
  onRefresh,
  count,
}) {
  const theme = useTheme()
  const big = useMediaQuery(theme.breakpoints.up('sm'))
  const classes = useStyles({ top: big ? 64 : 56 })
  const pos = useRef(0)
  const [show, setShow] = useState(true)

  useEffect(() => {
    function listener() {
      setShow(pos.current > window.scrollY)
      pos.current = window.scrollY
    }
    window.addEventListener('scroll', listener)
    return () => {
      window.removeEventListener('scroll', listener)
    }
  })

  return (
    <Card
      className={classes.root}
      elevation={4}
      style={{ position: show ? 'sticky' : 'static' }}
    >
      <CardContent>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={5}>
            <OrderingSelect ordering={ordering} setOrdering={onSetOrdering} />
          </Grid>
          <Grid item xs={4}>
            <SubredditSelect
              subreddit={subreddit}
              setSubreddit={onSetSubreddit}
            />
          </Grid>
          <Grid item xs={3}>
            <Button variant="outlined" onClick={onRefresh}>
              {count}
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}
