export const handler = async (event) => {
  const base = {
    Role: process.env.TRANSFER_USER_ROLE,
    HomeDirectory: `/${process.env.TRANSFER_BUCKET}/remote`,
    HomeDirectoryType: "PATH"
  };

  if (!event.password) {
    return {
      ...base,
      PublicKeys: [process.env.TRANSFER_USER_PUBLIC_KEY]
    };
  }

  if (event.password === process.env.TRANSFER_TEST_PASSWORD) {
    return base;
  }

  return {};
};
