import { FeatureFlag } from "./types";

let BACKEND =
  process.env.NODE_ENV === "production"
    ? process.env.REACT_APP_BACKEND_ADDR
    : "http://localhost:8555";

export function getAllFlagNames() {
  return fetch(`${BACKEND}/featureflag`).then((response) => response.json());
}

interface GetValueResponse {
  [key: string]: boolean;
}

export function getFeatureFlagValue(flag_name: string): Promise<GetValueResponse> {
  return fetch(`${BACKEND}/featureflag/${flag_name}`).then((resp) => resp.json());
}

export function createFeatureFlag(item: string) {
  return fetch(`${BACKEND}/featureflag/${item}`, {
    method: "POST",
  }).then((_) => {
    return fetch(`${BACKEND}/featureflag`).then((response) => response.json());
  });
}

export function deleteFeatureFlag(item: string) {
  return fetch(`${BACKEND}/featureflag/${item}`, {
    method: "DELETE",
  }).then((_) => {
    return fetch(`${BACKEND}/featureflag`).then((response) => response.json());
  });
}

export function refreshDataKeys(keys: string[]) {
  return Promise.all(
    keys.map((k) => {
      return fetch(`${BACKEND}/featureflag/${k}`)
        .then((resp) => resp.json())
        .then((val) => {
          console.log({ name: k, value: val });
          return { name: k, value: val[k] };
        });
    })
  );
}

export function switchFlag(item: FeatureFlag): Promise<GetValueResponse> {
  return fetch(`${BACKEND}/featureflag/${item.name}?value=${!item.value}`, {
    method: "PUT",
  }).then((_) => getFeatureFlagValue(item.name));
}
