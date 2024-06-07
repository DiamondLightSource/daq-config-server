import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  ChakraProvider,
  Checkbox,
  Grid,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  VStack,
  extendTheme,
} from "@chakra-ui/react";
import * as React from "react";
import { ColorModeSwitcher } from "./ColorModeSwitcher";

var BACKEND = "http://172.23.168.196:8555";
type FeatureFlag = { name: string; value: boolean };

let start_data = fetch(`${BACKEND}/featurelist/`).then((response) =>
  response.json()
);
var start_data_processed = false;

const theme = extendTheme({
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

export const App = () => {
  if (!start_data_processed) {
    start_data.then((data) => {
      resetDataKeys(data.sort());
      start_data_processed = true;
    });
  }

  const [feature_flag_data, setFeatureFlagData] = React.useState([
    { name: "empty", value: false },
  ]);
  function switchFlag(item: string) {
    let value = !getFeatureFlagData(item);
    fetch(`${BACKEND}/featureflag/${item}?value=${value}`, {
      method: "POST",
    }).then((_) =>
      fetch(`${BACKEND}/featureflag/${item}`)
        .then((resp) => resp.json())
        .then((val) => {
          console.log(`Updating ${item} based on response ${val}`);
          setFlag(item, val[item]);
        })
    );
  }
  function getFeatureFlagData(item: string) {
    for (let f of feature_flag_data) {
      if (f.name === item) {
        return f.value;
      }
    }
  }
  function setFlag(item: string, value: boolean) {
    setFeatureFlagData(
      feature_flag_data.map((i) =>
        i.name === item ? { name: item, value: value } : i
      )
    );
  }
  function resetDataKeys(keys: string[]) {
    return Promise.all(
      keys.map((k) => {
        return fetch(`${BACKEND}/featureflag/${k}`)
          .then((resp) => resp.json())
          .then((val) => {
            console.log({ name: k, value: val });
            return { name: k, value: val[k] };
          });
      })
    ).then((data) => setFeatureFlagData(data));
  }

  function propertyTableDatum(props: FeatureFlag) {
    return (
      <Tr key={props.name}>
        <Td>{props.name}</Td>
        <Td>
          <Checkbox
            isChecked={props.value}
            onChange={() => {
              switchFlag(props.name);
            }}
          ></Checkbox>
        </Td>
      </Tr>
    );
  }
  function doPropertyTableData(data: FeatureFlag[]) {
    return <Tbody>{data.map((item) => propertyTableDatum(item))}</Tbody>;
  }

  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">
        <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Text textStyle={"title"}>
              Read and store configuration for I03 Hyperion
            </Text>
            <Accordion defaultIndex={[0]} allowMultiple allowToggle>
              <AccordionItem>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    Feature flags
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  <TableContainer>
                    <Table variant="simple">
                      <TableCaption>
                        Control whether Hyperion features are turned on or off
                      </TableCaption>
                      <Thead>
                        <Tr>
                          <Th>Property</Th>
                          <Th>value</Th>
                        </Tr>
                      </Thead>
                      {doPropertyTableData(feature_flag_data)}
                    </Table>
                  </TableContainer>
                </AccordionPanel>
              </AccordionItem>
              <AccordionItem>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    Beamline parameters (not used by Hyperion or GDA, testing
                    only!)
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
                  do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                  Ut enim ad minim veniam, quis nostrud exercitation ullamco
                  laboris nisi ut aliquip ex ea commodo consequat.
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          </VStack>
        </Grid>
      </Box>
    </ChakraProvider>
  );
};
