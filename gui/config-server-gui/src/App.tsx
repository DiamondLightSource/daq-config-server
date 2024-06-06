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
  theme,
} from "@chakra-ui/react";
import * as React from "react";
import { ColorModeSwitcher } from "./ColorModeSwitcher";

type FeatureFlag = { name: string; value: boolean }


export const App = () => {

  const [test_data, setTestData] = React.useState([
    { name: "use_panda", value: false },
    { name: "use_gpu_for_PIA", value: false },
    { name: "test2", value: false },
    { name: "test3", value: true },
  ])
  function switchTestData(item: string) {
    setTestData(test_data.map((i) => i.name === item ? { name: item, value: !i.value } : i))
  }

  function propertyTableDatum(props: FeatureFlag) {
    return (
      <Tr key={props.name}>
        <Td>{props.name}</Td>
        <Td>
          <Checkbox
            isChecked={props.value}
            onChange={() => { switchTestData(props.name); }}
          >
          </Checkbox>
        </Td>
      </Tr >
    )
  }
  function doPropertyTableData(data: FeatureFlag[]) {
    return (
      <Tbody>
        {data.map(item => propertyTableDatum(item))}
      </Tbody>
    )
  }

  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">
        <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Text fontSize="3xl">
              Read and store configuration for I03 Hyperion
            </Text>
            <Accordion defaultIndex={[0]} allowMultiple allowToggle>
              <AccordionItem>
                <AccordionButton>
                  <Box as='span' flex='1' textAlign='left'>
                    Feature flags
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  <TableContainer>
                    <Table variant='simple'>
                      <TableCaption>Control whether Hyperion features are turned on or off</TableCaption>
                      <Thead>
                        <Tr>
                          <Th>Property</Th>
                          <Th>value</Th>
                          <Th>&nbsp;</Th>
                        </Tr>
                      </Thead>
                      {doPropertyTableData(test_data)}
                    </Table>
                  </TableContainer>
                </AccordionPanel>
              </AccordionItem>
              <AccordionItem>
                <AccordionButton>
                  <Box as='span' flex='1' textAlign='left'>
                    Beamline parameters (not used by Hyperion or GDA, testing only!)
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
                  tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
                  veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
                  commodo consequat.
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          </VStack>
        </Grid>
      </Box>
    </ChakraProvider>
  )

}