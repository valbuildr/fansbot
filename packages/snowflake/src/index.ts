import { SnowflakeIdGenerator } from "@codylabs/snowflake-id-generator";

export default new SnowflakeIdGenerator(1n, 1n, {
    epoch: 879096600000n // 9 November 1997 at 17:30 GMT
});