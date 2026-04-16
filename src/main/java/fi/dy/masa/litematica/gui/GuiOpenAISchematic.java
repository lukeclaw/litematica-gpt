package fi.dy.masa.litematica.gui;

import fi.dy.masa.litematica.data.DataManager;
import fi.dy.masa.litematica.schematic.ai.OpenAIIntegration;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicBuilder;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicDSLParser;
import fi.dy.masa.malilib.gui.GuiBase;
import fi.dy.masa.malilib.gui.GuiTextFieldGeneric;
import fi.dy.masa.malilib.gui.Message.MessageType;
import fi.dy.masa.malilib.gui.button.ButtonBase;
import fi.dy.masa.malilib.gui.button.ButtonGeneric;
import fi.dy.masa.malilib.gui.button.IButtonActionListener;
import fi.dy.masa.malilib.util.KeyCodes;
import net.minecraft.client.gui.DrawContext;

public class GuiOpenAISchematic extends GuiBase {

    private GuiTextFieldGeneric promptField;
    private GuiTextFieldGeneric nameField;
    private boolean isGenerating = false;

    public GuiOpenAISchematic() {
        this.title = "Generate AI Schematic";
    }

    @Override
    public void initGui() {
        super.initGui();
        
        int x = this.width / 2 - 150;
        int y = 50;
        
        this.promptField = new GuiTextFieldGeneric(x, y, 300, 20, this.textRenderer);
        this.promptField.setMaxLength(512);
        
        this.nameField = new GuiTextFieldGeneric(x, y + 40, 300, 20, this.textRenderer);
        this.nameField.setMaxLength(128);
        this.nameField.setText("ai-test.litematic");
        
        this.promptField.setFocused(true);

        ButtonGeneric generateButton = new ButtonGeneric(x, y + 80, 100, 20, "Generate");
        this.addButton(generateButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (isGenerating) return;
                
                String promptText = promptField.getText();
                String schemName = nameField.getText();

                if (promptText.isEmpty() || schemName.isEmpty()) {
                    addMessage(MessageType.ERROR, "Both fields are required!");
                    return;
                }

                addMessage(MessageType.INFO, "Generating schematic...");
                isGenerating = true;
                
                OpenAIIntegration.generateSchematic(promptText, null).thenAccept(script -> {
                    net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                        try {
                            System.out.println("AI Script: \n" + script);
                            boolean success = OpenAISchematicBuilder.buildAndSave(schemName, OpenAISchematicDSLParser.parse(script));
                            
                            if (success) {
                                addMessage(MessageType.SUCCESS, "Schematic built via AI successfully.");
                            } else {
                                addMessage(MessageType.ERROR, "Failed to compile the DSL script.");
                            }
                        } catch (Exception e) {
                            addMessage(MessageType.ERROR, "Crash while compiling script: " + e.getMessage());
                        } finally {
                            isGenerating = false;
                        }
                    });
                }).exceptionally(e -> {
                    net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                        addMessage(MessageType.ERROR, "API Failure: " + e.getMessage());
                        isGenerating = false;
                    });
                    return null;
                });
            }
        });
        
        ButtonGeneric cancelButton = new ButtonGeneric(x + 110, y + 80, 100, 20, "Cancel");
        this.addButton(cancelButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                GuiBase.openGui(new GuiMainMenu());
            }
        });
    }

    @Override
    public boolean onMouseClicked(int mouseX, int mouseY, int mouseButton) {
        if (this.promptField.mouseClicked(mouseX, mouseY, mouseButton)) return true;
        if (this.nameField.mouseClicked(mouseX, mouseY, mouseButton)) return true;
        return super.onMouseClicked(mouseX, mouseY, mouseButton);
    }

    @Override
    public boolean onKeyTyped(int keyCode, int scanCode, int modifiers) {
        if (this.promptField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.nameField.keyPressed(keyCode, scanCode, modifiers)) return true;
        
        if (keyCode == KeyCodes.KEY_TAB) {
            if (this.promptField.isFocused()) {
                this.promptField.setFocused(false);
                this.nameField.setFocused(true);
            } else {
                this.promptField.setFocused(true);
                this.nameField.setFocused(false);
            }
            return true;
        }

        return super.onKeyTyped(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean onCharTyped(char charIn, int modifiers) {
        if (this.promptField.charTyped(charIn, modifiers)) return true;
        if (this.nameField.charTyped(charIn, modifiers)) return true;
        return super.onCharTyped(charIn, modifiers);
    }

    @Override
    public void drawContents(DrawContext drawContext, int mouseX, int mouseY, float partialTicks) {
        super.drawContents(drawContext, mouseX, mouseY, partialTicks);
        
        int x = this.width / 2 - 150;
        int y = 50;

        drawContext.drawText(this.textRenderer, "Prompt (Describe your build):", x, y - 10, 0xFFFFFF, true);
        this.promptField.render(drawContext, mouseX, mouseY, partialTicks);
        
        drawContext.drawText(this.textRenderer, "Output File Name:", x, y + 30, 0xFFFFFF, true);
        this.nameField.render(drawContext, mouseX, mouseY, partialTicks);
        
        if (isGenerating) {
            drawContext.drawText(this.textRenderer, "Generating... Please wait.", x, y + 120, 0xFFFF00, true);
        }
    }
}
