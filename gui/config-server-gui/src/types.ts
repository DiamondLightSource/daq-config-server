export type FeatureFlag = { name: string; value: boolean };
export type SetLocalFeatureFlagData = React.Dispatch<
  React.SetStateAction<
    {
      name: string;
      value: boolean;
    }[]
  >
>;
export type LocalFlagDataHook = {
  data: FeatureFlag[];
  setData: SetLocalFeatureFlagData;
};
