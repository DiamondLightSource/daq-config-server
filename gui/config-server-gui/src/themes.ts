import { extendTheme } from "@chakra-ui/react";

export const theme = extendTheme({
  textStyles: {
    title: {
      fontSize: "3xl",
      fontWeight: "bold",
      lineHeight: "120%",
      textDecoration: "underline",
      letterSpacing: "-8%",
    },
  },
});
