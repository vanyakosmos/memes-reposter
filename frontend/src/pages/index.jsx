import React from "react"

import { makeStyles } from "@material-ui/core/styles"
import Card from "@material-ui/core/Card"
import CardHeader from "@material-ui/core/CardHeader"
import CardContent from "@material-ui/core/CardContent"
import Typography from "@material-ui/core/Typography"
import Layout from "../components/Layout"

const useStyles = makeStyles({
  card: {
    marginBottom: 20,
  }
})

const IndexPage = () => {
  const classes = useStyles()
  
  return (
    <Layout>
      <Card className={classes.card}>
        <CardHeader title="Publish" />
        <CardContent>
          <Typography variant="body2" component="p">
            reddit
          </Typography>
          <Typography variant="body2" component="p">
            imgur
          </Typography>
          <Typography variant="body2" component="p">
            rss
          </Typography>
        </CardContent>
      </Card>
      <Card className={classes.card}>
        <CardHeader title="Clean Up" />
        <CardContent>
          <Typography variant="body2" component="p">
            reddit
          </Typography>
        </CardContent>
      </Card>
    </Layout>
  )
}

export default IndexPage
