import FormControl from '@material-ui/core/FormControl'
import Grid from '@material-ui/core/Grid'
import InputLabel from '@material-ui/core/InputLabel'
import MenuItem from '@material-ui/core/MenuItem'
import Select from '@material-ui/core/Select'
import { makeStyles } from '@material-ui/styles'
import React, { useEffect, useState } from 'react'
import { getRedditPosts } from 'src/apiClient'
import Layout from 'src/components/Layout'
import Post from 'src/components/Post'

const useStyles = makeStyles({
  filters: {
    marginBottom: 20,
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
    setSubs(['memes']) // todo
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

const IndexPage = () => {
  const classes = useStyles()
  const [posts, setPosts] = useState([])
  const [ordering, setOrdering] = useState('created')
  const [subreddit, setSubreddit] = useState('-')

  console.log(subreddit, ordering)

  useEffect(() => {
    const sub = subreddit === '-' ? '' : subreddit
    getRedditPosts(sub, ordering).then(posts => {
      setPosts(posts.slice(0, 5))
    })
  }, [ordering, subreddit])

  return (
    <Layout>
      <div className={classes.filters}>
        <Grid container spacing={2}>
          <Grid item xs={6}>
            <OrderingSelect ordering={ordering} setOrdering={setOrdering} />
          </Grid>
          <Grid item xs={6}>
            <SubredditSelect
              subreddit={subreddit}
              setSubreddit={setSubreddit}
            />
          </Grid>
        </Grid>
      </div>
      <div>
        {posts.map(p => (
          <Post key={p.id} {...p} />
        ))}
      </div>
    </Layout>
  )
}

export default IndexPage
