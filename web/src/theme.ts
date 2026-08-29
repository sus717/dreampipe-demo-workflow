import { alpha, createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#080d12', paper: '#101820' },
    primary: { main: '#f2ad3d', contrastText: '#1d1303' },
    secondary: { main: '#42d6ba' },
    success: { main: '#72d678' },
    warning: { main: '#f2ad3d' },
    error: { main: '#ff5d5d' },
    text: { primary: '#f1f4f3', secondary: '#91a0aa' },
    divider: alpha('#c9d7df', 0.12),
  },
  typography: {
    fontFamily: '"Avenir Next", "PingFang SC", "Hiragino Sans GB", sans-serif',
    h1: { fontWeight: 780, letterSpacing: '-0.045em' },
    h2: { fontWeight: 720, letterSpacing: '-0.03em' },
    h3: { fontWeight: 680, letterSpacing: '-0.02em' },
    button: { fontWeight: 720, textTransform: 'none' },
  },
  shape: { borderRadius: 14 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { minHeight: 38, boxShadow: 'none' },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 650, letterSpacing: '0.01em' },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
  },
})
