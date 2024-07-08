import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  Box,
  Button,
  ChakraProvider,
  Checkbox,
  Grid,
  Input,
  InputGroup,
  InputRightElement,
  Popover,
  PopoverArrow,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
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
  useDisclosure,
} from "@chakra-ui/react";
import * as React from "react";
import { ColorModeSwitcher } from "./ColorModeSwitcher";
import {
  createFeatureFlag,
  deleteFeatureFlag,
  getAllFlagNames,
  refreshDataKeys,
  switchFlag,
} from "./communication";
import { theme } from "./themes";
import { FeatureFlag, LocalFlagDataHook, SetLocalFeatureFlagData } from "./types";

const start_data = getAllFlagNames();

function setLocalFlag(item: string, value: boolean, local_data_hook: LocalFlagDataHook) {
  local_data_hook.setData(
    local_data_hook.data.map((i) => (i.name === item ? { name: item, value: value } : i))
  );
}

//** A button which triggers deletion of a flag */
const DeleteFlagButton = ({
  item,
  setFeatureFlagData,
}: {
  item: string;
  setFeatureFlagData: SetLocalFeatureFlagData;
}) => (
  <Button
    onClick={() =>
      deleteFeatureFlag(item)
        .then((data) => refreshDataKeys(data.sort()))
        .then((data) => setFeatureFlagData(data))
    }
  >
    delete
  </Button>
);

//** Generate PropertyTableDatum elements for every item */
const PropertyTableData = ({ data }: { data: LocalFlagDataHook }) => (
  <Tbody>
    {data.data.map((item) => (
      <PropertyTableDatum flag={item} data={data} key={item.name} />
    ))}
    <Tr>
      <Td colSpan={3} textAlign={"center"}>
        <CreateNewPopover local_data_hook={data} />
      </Td>
    </Tr>
  </Tbody>
);

/** A single row in the table of feature flags */
const PropertyTableDatum = ({ flag, data }: { flag: FeatureFlag; data: LocalFlagDataHook }) => (
  <Tr key={flag.name}>
    <Td>{flag.name}</Td>
    <Td>
      <Checkbox
        isChecked={flag.value}
        onChange={() => {
          switchFlag(flag).then((resp) => {
            setLocalFlag(flag.name, resp[flag.name], data);
            console.info(`Updating ${flag.name} based on response ${resp}`);
          });
        }}
      ></Checkbox>
    </Td>
    <Td>
      <DeleteFlagButton item={flag.name} setFeatureFlagData={data.setData} />
    </Td>
  </Tr>
);

/** A text field with a submit button for creating new feature flags */
const CreateFeatureSubmit = ({
  closeDialog,
  local_data_hook,
}: {
  closeDialog: Function | null;
  local_data_hook: LocalFlagDataHook;
}) => {
  const [value, setValue] = React.useState("");
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value);
  const submitCreateFlag = () => {
    createFeatureFlag(value)
      .then((data) => refreshDataKeys(data.sort()))
      .then((data) => local_data_hook.setData(data));
    setValue("");
    if (closeDialog !== null) {
      closeDialog();
    }
  };
  return (
    <>
      <InputGroup width="100%">
        <Input
          placeholder="flag_name"
          size="md"
          onChange={handleChange}
          onKeyDown={(event) => event.key === "Enter" && submitCreateFlag()}
        ></Input>
        <InputRightElement
          children={
            <Button onClick={submitCreateFlag} size="xs">
              create
            </Button>
          }
          width="15%"
        ></InputRightElement>
      </InputGroup>
    </>
  );
};

/** A popover for creating new feature flags */
const CreateNewPopover = ({ local_data_hook }: { local_data_hook: LocalFlagDataHook }) => {
  const { isOpen, onToggle, onClose } = useDisclosure();
  return (
    <Popover onClose={onClose} isOpen={isOpen} arrowSize={15}>
      <PopoverTrigger>
        <Button onClick={onToggle}>Create new</Button>
      </PopoverTrigger>
      <PopoverContent maxW="xxl" minW="lg">
        <PopoverHeader fontSize={"medium"}>Create new feature flag</PopoverHeader>
        <PopoverArrow />
        <PopoverCloseButton />
        <PopoverBody>
          <CreateFeatureSubmit closeDialog={onClose} local_data_hook={local_data_hook} />
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export const App = () => {
  const [feature_flag_data, setFeatureFlagData] = React.useState([{ name: "empty", value: false }]);

  React.useEffect(() => {
    start_data
      .then((data) => refreshDataKeys(data.sort()))
      .then((data) => setFeatureFlagData(data));
  }, []);

  return (
    <ChakraProvider theme={theme}>
      <Box textAlign="center" fontSize="xl">
        <Grid minH="100vh" p={3}>
          <ColorModeSwitcher justifySelf="flex-end" />
          <VStack spacing={8}>
            <Text textStyle={"title"}>Read and store configuration for I03 Hyperion</Text>
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
                          <Th>&nbsp;</Th>
                        </Tr>
                      </Thead>
                      <PropertyTableData
                        data={{
                          data: feature_flag_data,
                          setData: setFeatureFlagData,
                        }}
                      />
                    </Table>
                  </TableContainer>
                </AccordionPanel>
              </AccordionItem>
              <AccordionItem>
                <AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    Beamline parameters (not used by Hyperion or GDA, testing only!)
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
                <AccordionPanel pb={4}>
                  Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                  incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
                  exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                </AccordionPanel>
              </AccordionItem>
            </Accordion>
          </VStack>
        </Grid>
      </Box>
    </ChakraProvider>
  );
};
