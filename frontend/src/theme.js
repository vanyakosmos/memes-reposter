import { deepOrange, indigo, red } from "@material-ui/core/colors"
import { createMuiTheme } from "@material-ui/core/styles"

const theme = createMuiTheme({
    palette: {
      type: "dark",
      primary: indigo,
      secondary: deepOrange,
      error: red,
      background: {
        default: "#272c2f",
      },
    },
    shape: {
      borderRadius: 10,
    },
  },
)

console.log(theme)
export default theme
