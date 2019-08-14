import { red } from "@material-ui/core/colors"
import { createMuiTheme } from "@material-ui/core/styles"

const theme = createMuiTheme({
    palette: {
      text: {
        primary: '#e8e8e8',
        secondary: '#d9d9d9',
        disabled: '#aeaeae',
        hint: '#e8e8e8',
      },
      background: {
        default: "#272c2f",
        paper: "#353c40",
      },
      divider: '#e8e8e8',
      action: {
        active: '#e8e8e8',
      },
      primary: {
        main: '#1b1f21',
        contrastText: '#e8e8e8',
      },
      secondary: {
        main: '#27a5ff',
      },
      error: red,
    },
    shape: {
      borderRadius: 10,
    },
  },
)

console.log(theme)
export default theme
