-- migrate:up
create procedure _add_example_data_2 ()
  comment 'Add real arrow data for job'
  modifies sql data
begin
  set @jobdataid1 = uuid_to_bin('f9ef0c00-43ac-11eb-8931-f4939feddd82', 1);
  set @modtime = timestamp('2020-12-11 20:00');
  update job_data set
    present = true,
    format = 'application/vnd.apache.arrow.file',
    filename = 'inverter_0_performance.arrow',
    modified_at = @modtime ,
    data = from_base64('
QVJST1cxAAD/////gAIAABAAAAAAAAoADgAGAAUACAAKAAAAAAEEABAAAAAAAAoADAAAAAQACAAK
AAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAAAHBhbmRhcwAAhwEAAHsi
aW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwgImNvbHVtbnMiOiBbeyJu
YW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRhc190eXBlIjogImRhdGV0
aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJtZXRhZGF0YSI6IHsidGlt
ZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAiZmllbGRfbmFtZSI6ICJw
ZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1weV90eXBlIjogImludDY0
IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFyeSI6ICJweWFycm93Iiwg
InZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEuMS40In0AAgAAAFQAAAAE
AAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNlAAgADAAIAAcACAAAAAAA
AAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAAAAAAAAQAAAB0aW1lAAAA
AAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwD/////yAAAABQAAAAAAAAADAAYAAYABQAIAAwA
DAAAAAADBAAcAAAAUAAAAAAAAAAAAAAADAAcABAABAAIAAwADAAAAGgAAAAcAAAAFAAAAAIAAAAA
AAAAAAAAAAQABAAEAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACcAAAAAAAAAKAAAAAAA
AAAAAAAAAAAAACgAAAAAAAAAJAAAAAAAAAAAAAAAAgAAAAIAAAAAAAAAAAAAAAAAAAACAAAAAAAA
AAAAAAAAAAAAEAAAAAAAAAAEIk0YYECCEAAAgAAAirk1muUVAKBC6nud5RUAAAAAABAAAAAAAAAA
BCJNGGBAgg0AAAATAAEAgAEAAAAAAAAAAAAAAAAAAAD/////AAAAABAAAAAMABQABgAIAAwAEAAM
AAAAAAAEAEAAAAAoAAAABAAAAAEAAACQAgAAAAAAANAAAAAAAAAAUAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAoADAAAAAQACAAKAAAAvAEAAAQAAAABAAAADAAAAAgADAAEAAgACAAAAAgAAAAQAAAABgAA
AHBhbmRhcwAAhwEAAHsiaW5kZXhfY29sdW1ucyI6IFtdLCAiY29sdW1uX2luZGV4ZXMiOiBbXSwg
ImNvbHVtbnMiOiBbeyJuYW1lIjogInRpbWUiLCAiZmllbGRfbmFtZSI6ICJ0aW1lIiwgInBhbmRh
c190eXBlIjogImRhdGV0aW1ldHoiLCAibnVtcHlfdHlwZSI6ICJkYXRldGltZTY0W25zXSIsICJt
ZXRhZGF0YSI6IHsidGltZXpvbmUiOiAiVVRDIn19LCB7Im5hbWUiOiAicGVyZm9ybWFuY2UiLCAi
ZmllbGRfbmFtZSI6ICJwZXJmb3JtYW5jZSIsICJwYW5kYXNfdHlwZSI6ICJpbnQ2NCIsICJudW1w
eV90eXBlIjogImludDY0IiwgIm1ldGFkYXRhIjogbnVsbH1dLCAiY3JlYXRvciI6IHsibGlicmFy
eSI6ICJweWFycm93IiwgInZlcnNpb24iOiAiMi4wLjAifSwgInBhbmRhc192ZXJzaW9uIjogIjEu
MS40In0AAgAAAFQAAAAEAAAAxP///wAAAQIQAAAAJAAAAAQAAAAAAAAACwAAAHBlcmZvcm1hbmNl
AAgADAAIAAcACAAAAAAAAAFAAAAAEAAUAAgABgAHAAwAAAAQABAAAAAAAAEKEAAAACAAAAAEAAAA
AAAAAAQAAAB0aW1lAAAAAAgADAAGAAgACAAAAAAAAwAEAAAAAwAAAFVUQwCwAgAAQVJST1cx
')
   where id = @jobdataid1;
end;


drop procedure add_example_data;
create procedure add_example_data ()
  modifies sql data
begin
  CALL _add_example_data_0;
  CALL _add_example_data_1;
  CALL _add_example_data_2;
end;


-- migrate:down
drop procedure add_example_data;
create procedure add_example_data ()
  modifies sql data
begin
  CALL _add_example_data_0;
  CALL _add_example_data_1;
end;

drop procedure _add_example_data_2;
