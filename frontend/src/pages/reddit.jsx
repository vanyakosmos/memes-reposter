import { makeStyles } from '@material-ui/styles'
import React, { useEffect, useState } from 'react'
import { getRedditPosts } from 'src/apiClient'
import Filters from 'src/components/Filters'
import Layout from 'src/components/Layout'
import Post from 'src/components/Post'

const useStyles = makeStyles(() => ({
  root: {
    position: 'relative',
  },
}))

export default function RedditPage() {
  const classes = useStyles()
  const [count, setCount] = useState('-')
  const [posts, setPosts] = useState([])
  const [ordering, setOrdering] = useState(
    localStorage.getItem('reddit:ordering') || 'created',
  )
  const [subreddit, setSubreddit] = useState('-')

  useEffect(() => {
    handleRefresh()
  }, [ordering, subreddit])

  function handleSetOrdering(ordering) {
    window.scrollTo({ top: 0 })
    localStorage.setItem('reddit:ordering', ordering)
    setOrdering(ordering)
  }

  function handleSetSubreddit(sub) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    setSubreddit(sub)
  }

  function handleRefresh() {
    const sub = subreddit === '-' ? '' : subreddit
    getRedditPosts(sub, ordering).then(({ posts, count }) => {
      setPosts(posts.slice(0, 5))
      setCount(count)
    })
  }

  return (
    <Layout>
      <div className={classes.root}>
        <Filters
          ordering={ordering}
          onSetOrdering={handleSetOrdering}
          subreddit={subreddit}
          onSetSubreddit={handleSetSubreddit}
          onRefresh={handleRefresh}
          count={count}
        />
        <div>
          {posts.map(p => (
            <Post key={p.id} {...p} />
          ))}
        </div>
      </div>
    </Layout>
  )
}
