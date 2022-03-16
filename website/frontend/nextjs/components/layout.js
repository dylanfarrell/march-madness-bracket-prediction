import ResponsiveAppBar from './header'

export default function Layout({ children }) {
  return (
    <>
      <ResponsiveAppBar />
      <main>{children}</main>
    </>
  )
}